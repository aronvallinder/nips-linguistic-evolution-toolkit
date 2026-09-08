import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import hf_sync_completed_runs as hf_sync
from src.experiment_condition import build_condition, digest
from src.llm_settings import resolve_request_plan


REQUEST = resolve_request_plan("openai/gpt-5-nano", {
    "provider": "direct", "reasoning": {"reasoning_effort": "low"},
    "temperature": "default", "max_output_tokens": 128,
}, {}).as_dict()
CONDITION = build_condition(SimpleNamespace(), None, {"llm_request": REQUEST}, {})


FULL_STATE = {
    "agents": {},
    "conversation_history": [],
    "game_data": {},
    "task_order": ["game"],
    "run_metadata": {
        "llm_provider": "openai", "provider_model": "gpt-5-nano", "llm_request": REQUEST,
        "experiment_condition": CONDITION, "condition_sha256": digest(CONDITION),
    },
}


def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_discovery_accepts_only_full_final_state_json(tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)
    write_json(data_root / "experiment" / "run.results.json", FULL_STATE)
    write_json(data_root / "experiment" / "run.checkpoint.json", FULL_STATE)
    write_json(data_root / "experiment" / "run.checkpoint.json.error.json", FULL_STATE)
    write_json(
        data_root / "experiment" / "analysis.json",
        {"metadata": {}, "trials": []},
    )
    invalid = data_root / "experiment" / "truncated.json"
    invalid.write_text("{", encoding="utf-8")

    discovered = hf_sync.discover_completed_final_jsons(
        [data_root],
        data_root=data_root,
    )

    assert discovered == (final.resolve(),)


def test_plan_allows_only_artifacts_gated_by_a_final_json(tmp_path):
    data_root = tmp_path / "data" / "json"
    run_dir = data_root / "noise_experiments" / "example" / "model"
    final = write_json(run_dir / "run.json", FULL_STATE)
    results = write_json(run_dir / "run.results.json", {"game_data": {}})
    log = run_dir / "run.log"
    log.write_text("complete", encoding="utf-8")
    transcript = run_dir / "run.transcript.pdf"
    transcript.write_bytes(b"%PDF-complete")

    write_json(run_dir / "failed.results.json", {"game_data": {}})
    (run_dir / "failed.log").write_text("partial", encoding="utf-8")
    write_json(run_dir / "failed.checkpoint.json.error.json", FULL_STATE)

    plan = hf_sync.build_upload_plan(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
    )

    assert plan.final_paths == (final.resolve(),)
    assert set(plan.artifact_paths) == {
        final.resolve(),
        results.resolve(),
        log.resolve(),
        transcript.resolve(),
    }
    assert set(plan.remote_paths) == {
        "uploaders/uploader/data/json/noise_experiments/example/model/run.json",
        "uploaders/uploader/data/json/noise_experiments/example/model/run.results.json",
        "uploaders/uploader/data/json/noise_experiments/example/model/run.log",
        "uploaders/uploader/data/json/noise_experiments/example/model/run.transcript.pdf",
    }
    assert not any("failed" in path for path in plan.remote_paths)


def test_plan_rejects_symlinked_companion_outside_data_root(tmp_path):
    data_root = tmp_path / "data" / "json"
    run_dir = data_root / "experiment"
    final = write_json(run_dir / "run.json", FULL_STATE)
    outside_secret = tmp_path / "outside.env"
    outside_secret.write_text("HF_TOKEN=do-not-upload", encoding="utf-8")
    symlinked_log = run_dir / "run.log"
    symlinked_log.symlink_to(outside_secret)

    plan = hf_sync.build_upload_plan(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
    )

    assert plan.artifact_paths == (final.resolve(),)
    assert symlinked_log not in plan.artifact_paths
    assert outside_secret.resolve() not in plan.artifact_paths


def test_sync_uses_one_locked_exact_commit(tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)
    log = data_root / "experiment" / "run.log"
    log.write_text("complete", encoding="utf-8")
    calls = []

    class FakeApi:
        def repo_info(self, **kwargs):
            assert kwargs == {"repo_id": "owner/dataset", "repo_type": "dataset"}
            return SimpleNamespace(sha="remote-head", private=True)

        def create_commit(self, **kwargs):
            calls.append(kwargs)

    lock_path = tmp_path / "sync.lock"
    plan = hf_sync.sync_completed_runs(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
        lock_path=lock_path,
        api=FakeApi(),
        label="example",
    )

    assert lock_path.exists()
    assert len(calls) == 1
    assert calls[0]["repo_id"] == "owner/dataset"
    assert calls[0]["repo_type"] == "dataset"
    assert {
        operation.path_in_repo for operation in calls[0]["operations"]
    } == {
        "uploaders/uploader/data/json/experiment/run.json",
        "uploaders/uploader/data/json/experiment/run.log",
    }
    assert calls[0]["parent_commit"] == "remote-head"


def test_local_upload_lock_uses_windows_fallback(monkeypatch, tmp_path):
    class FakeMsvcrt:
        LK_NBLCK = 1
        LK_UNLCK = 2

        def __init__(self):
            self.calls = []

        def locking(self, file_descriptor, mode, byte_count):
            self.calls.append((file_descriptor, mode, byte_count))

    fake_msvcrt = FakeMsvcrt()
    monkeypatch.setattr(hf_sync, "_fcntl", None)
    monkeypatch.setattr(hf_sync, "_msvcrt", fake_msvcrt)

    with hf_sync.local_upload_lock(tmp_path / "sync.lock"):
        pass

    assert [call[1:] for call in fake_msvcrt.calls] == [
        (fake_msvcrt.LK_NBLCK, 1),
        (fake_msvcrt.LK_UNLCK, 1),
    ]


def test_commit_chunks_keep_completed_run_families_atomic(monkeypatch, tmp_path):
    data_root = tmp_path / "data" / "json"
    first_final = write_json(data_root / "experiment" / "first.json", FULL_STATE)
    write_json(
        data_root / "experiment" / "first.results.json",
        {"game_data": {}},
    )
    (data_root / "experiment" / "first.log").write_text(
        "complete",
        encoding="utf-8",
    )
    (data_root / "experiment" / "first.transcript.pdf").write_bytes(
        b"%PDF-first"
    )
    second_final = write_json(data_root / "experiment" / "second.json", FULL_STATE)
    write_json(
        data_root / "experiment" / "second.results.json",
        {"game_data": {}},
    )
    (data_root / "experiment" / "second.log").write_text(
        "complete",
        encoding="utf-8",
    )
    (data_root / "experiment" / "second.transcript.pdf").write_bytes(
        b"%PDF-second"
    )
    commits = []

    class FakeApi:
        def repo_info(self, **kwargs):
            return SimpleNamespace(sha=f"head-{len(commits)}", private=True)

        def create_commit(self, **kwargs):
            commits.append(
                sorted(operation.path_in_repo for operation in kwargs["operations"])
            )

    monkeypatch.setattr(hf_sync, "MAX_COMMIT_OPERATIONS", 5)

    hf_sync.sync_completed_runs(
        [first_final, second_final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
        lock_path=tmp_path / "sync.lock",
        api=FakeApi(),
    )

    assert commits == [
        [
            "uploaders/uploader/data/json/experiment/first.json",
            "uploaders/uploader/data/json/experiment/first.log",
            "uploaders/uploader/data/json/experiment/first.results.json",
            "uploaders/uploader/data/json/experiment/first.transcript.pdf",
        ],
        [
            "uploaders/uploader/data/json/experiment/second.json",
            "uploaders/uploader/data/json/experiment/second.log",
            "uploaders/uploader/data/json/experiment/second.results.json",
            "uploaders/uploader/data/json/experiment/second.transcript.pdf",
        ],
    ]


def test_chunk_manifest_contains_every_approved_artifact_exactly_once(
    monkeypatch,
    tmp_path,
):
    data_root = tmp_path / "data" / "json"
    finals = []
    for name in ("first", "second", "third"):
        final = write_json(data_root / "experiment" / f"{name}.json", FULL_STATE)
        write_json(
            data_root / "experiment" / f"{name}.results.json",
            {"game_data": {}},
        )
        (data_root / "experiment" / f"{name}.log").write_text(
            "complete",
            encoding="utf-8",
        )
        finals.append(final)

    plan = hf_sync.build_upload_plan(
        finals,
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
    )
    monkeypatch.setattr(hf_sync, "MAX_COMMIT_OPERATIONS", 4)

    chunks = hf_sync._artifact_group_chunks(plan)
    chunk_artifacts = [
        path
        for chunk in chunks
        for group in chunk
        for path in group
    ]

    assert len(chunk_artifacts) == len(set(chunk_artifacts))
    assert set(chunk_artifacts) == set(plan.artifact_paths)
    assert all(group[0] in plan.final_paths for chunk in chunks for group in chunk)


def test_chunking_enforces_raw_byte_cap_without_splitting_families(
    monkeypatch,
    tmp_path,
):
    data_root = tmp_path / "data" / "json"
    finals = []
    for name in ("first", "second"):
        final = write_json(data_root / "experiment" / f"{name}.json", FULL_STATE)
        (data_root / "experiment" / f"{name}.log").write_bytes(b"x" * 200)
        finals.append(final)

    plan = hf_sync.build_upload_plan(
        finals,
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
    )
    group_sizes = [
        sum(path.stat().st_size for path in group)
        for group in hf_sync._artifact_groups(plan)
    ]
    byte_cap = max(group_sizes)
    assert hf_sync.MAX_COMMIT_OPERATIONS <= 100
    assert hf_sync.MAX_COMMIT_RAW_BYTES == 500 * 1024 * 1024
    monkeypatch.setattr(hf_sync, "MAX_COMMIT_RAW_BYTES", byte_cap)

    chunks = hf_sync._artifact_group_chunks(plan)

    assert len(chunks) == 2
    assert all(
        sum(path.stat().st_size for group in chunk for path in group) <= byte_cap
        for chunk in chunks
    )


def test_oversized_run_family_is_rejected_instead_of_split(monkeypatch, tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)
    log = data_root / "experiment" / "run.log"
    log.write_bytes(b"x" * 200)
    plan = hf_sync.build_upload_plan(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
    )
    family_bytes = sum(path.stat().st_size for path in plan.artifact_paths)
    monkeypatch.setattr(hf_sync, "MAX_COMMIT_RAW_BYTES", family_bytes - 1)

    with pytest.raises(RuntimeError, match="refusing to split a final JSON"):
        hf_sync._artifact_group_chunks(plan)


def test_uploader_namespaces_have_disjoint_reserved_remote_paths(tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    aron_plan = hf_sync.build_upload_plan(
        [final],
        repo_id="owner/dataset",
        namespace="aron",
        data_root=data_root,
    )
    ivar_plan = hf_sync.build_upload_plan(
        [final],
        repo_id="owner/dataset",
        namespace="ivar",
        data_root=data_root,
    )

    assert set(aron_plan.remote_paths).isdisjoint(ivar_plan.remote_paths)
    assert aron_plan.remote_paths == (
        "uploaders/aron/data/json/experiment/run.json",
    )
    assert ivar_plan.remote_paths == (
        "uploaders/ivar/data/json/experiment/run.json",
    )


@pytest.mark.parametrize("status_code", [409, 412])
def test_remote_conflict_refreshes_head_and_retries(
    monkeypatch,
    tmp_path,
    status_code,
):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    class ConflictError(RuntimeError):
        def __init__(self, status_code):
            super().__init__(f"conflict {status_code}")
            self.response = SimpleNamespace(status_code=status_code)

    class FakeApi:
        def __init__(self):
            self.heads = iter(["old-head", "new-head"])
            self.uploads = []
            self.operation_id_sets = []

        def repo_info(self, **kwargs):
            return SimpleNamespace(sha=next(self.heads), private=True)

        def create_commit(self, **kwargs):
            self.uploads.append(kwargs)
            self.operation_id_sets.append(
                {id(operation) for operation in kwargs["operations"]}
            )
            if len(self.uploads) == 1:
                for operation in kwargs["operations"]:
                    operation._is_committed = True
                raise ConflictError(status_code)

    api = FakeApi()
    delays = []
    monkeypatch.setattr(hf_sync.time, "sleep", delays.append)
    hf_sync.sync_completed_runs(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
        lock_path=tmp_path / "sync.lock",
        api=api,
    )

    assert [call["parent_commit"] for call in api.uploads] == [
        "old-head",
        "new-head",
    ]
    assert api.operation_id_sets[0].isdisjoint(api.operation_id_sets[1])
    assert delays == [1]


def test_nested_connection_error_refreshes_head_and_retries(monkeypatch, tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    class ProtocolError(RuntimeError):
        pass

    ProtocolError.__module__ = "urllib3.exceptions"

    class FakeApi:
        def __init__(self):
            self.calls = []
            self.repo_info_calls = 0

        def repo_info(self, **kwargs):
            self.repo_info_calls += 1
            return SimpleNamespace(
                sha=f"head-{self.repo_info_calls}",
                private=True,
            )

        def create_commit(self, **kwargs):
            self.calls.append(kwargs)
            if len(self.calls) == 1:
                raise ProtocolError(
                    "connection aborted",
                    OSError(hf_sync.errno.EADDRNOTAVAIL, "address unavailable"),
                )

    api = FakeApi()
    delays = []
    monkeypatch.setattr(hf_sync.time, "sleep", delays.append)

    hf_sync.sync_completed_runs(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
        lock_path=tmp_path / "sync.lock",
        api=api,
    )

    assert [call["parent_commit"] for call in api.calls] == ["head-1", "head-2"]
    assert delays == [1]


def test_repo_info_connection_error_is_retried(monkeypatch, tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    class FakeApi:
        def __init__(self):
            self.repo_info_calls = 0
            self.commit_calls = 0

        def repo_info(self, **kwargs):
            self.repo_info_calls += 1
            if self.repo_info_calls == 1:
                raise OSError(
                    hf_sync.errno.EADDRNOTAVAIL,
                    "address unavailable",
                )
            return SimpleNamespace(sha="fresh-head", private=True)

        def create_commit(self, **kwargs):
            self.commit_calls += 1

    api = FakeApi()
    delays = []
    monkeypatch.setattr(hf_sync.time, "sleep", delays.append)

    hf_sync.sync_completed_runs(
        [final],
        repo_id="owner/dataset",
        namespace="uploader",
        data_root=data_root,
        lock_path=tmp_path / "sync.lock",
        api=api,
    )

    assert api.repo_info_calls == 2
    assert api.commit_calls == 1
    assert delays == [1]


@pytest.mark.parametrize("status_code", [408, 425, 429, 500, 503, 599])
def test_transient_http_statuses_are_retryable(status_code):
    class HttpError(RuntimeError):
        def __init__(self):
            super().__init__(f"HTTP {status_code}")
            self.response = SimpleNamespace(status_code=status_code)

    assert hf_sync._is_transient_upload_error(HttpError()) is True


def test_terminal_http_status_overrides_nested_connection_error():
    class AuthenticationError(RuntimeError):
        response = SimpleNamespace(status_code=401)

    error = AuthenticationError("denied")
    error.__cause__ = ConnectionError("stale socket context")

    assert hf_sync._is_transient_upload_error(error) is False


def test_privacy_is_rechecked_between_commit_chunks(monkeypatch, tmp_path):
    data_root = tmp_path / "data" / "json"
    first_final = write_json(data_root / "experiment" / "first.json", FULL_STATE)
    second_final = write_json(data_root / "experiment" / "second.json", FULL_STATE)
    commits = []

    class FakeApi:
        def __init__(self):
            self.repo_info_calls = 0

        def repo_info(self, **kwargs):
            self.repo_info_calls += 1
            return SimpleNamespace(
                sha=f"head-{self.repo_info_calls}",
                private=self.repo_info_calls == 1,
            )

        def create_commit(self, **kwargs):
            commits.append(
                [operation.path_in_repo for operation in kwargs["operations"]]
            )

    monkeypatch.setattr(hf_sync, "MAX_COMMIT_OPERATIONS", 1)
    with pytest.raises(RuntimeError, match="refusing to upload to public dataset"):
        hf_sync.sync_completed_runs(
            [first_final, second_final],
            repo_id="owner/dataset",
            namespace="uploader",
            data_root=data_root,
            lock_path=tmp_path / "sync.lock",
            api=FakeApi(),
        )

    assert commits == [
        ["uploaders/uploader/data/json/experiment/first.json"]
    ]


def test_mid_backfill_failure_leaves_only_complete_run_families(
    monkeypatch,
    tmp_path,
):
    data_root = tmp_path / "data" / "json"
    finals = []
    for name in ("first", "second"):
        final = write_json(data_root / "experiment" / f"{name}.json", FULL_STATE)
        write_json(
            data_root / "experiment" / f"{name}.results.json",
            {"game_data": {}},
        )
        (data_root / "experiment" / f"{name}.log").write_text(
            "complete",
            encoding="utf-8",
        )
        (data_root / "experiment" / f"{name}.transcript.pdf").write_bytes(
            b"%PDF-complete"
        )
        finals.append(final)

    visible_commits = []

    class FakeApi:
        def repo_info(self, **kwargs):
            return SimpleNamespace(sha=f"head-{len(visible_commits)}", private=True)

        def create_commit(self, **kwargs):
            paths = {operation.path_in_repo for operation in kwargs["operations"]}
            if visible_commits:
                raise RuntimeError("network unavailable")
            visible_commits.append(paths)

    monkeypatch.setattr(hf_sync, "MAX_COMMIT_OPERATIONS", 4)
    with pytest.raises(RuntimeError, match="network unavailable"):
        hf_sync.sync_completed_runs(
            finals,
            repo_id="owner/dataset",
            namespace="uploader",
            data_root=data_root,
            lock_path=tmp_path / "sync.lock",
            api=FakeApi(),
        )

    assert visible_commits == [
        {
            "uploaders/uploader/data/json/experiment/first.json",
            "uploaders/uploader/data/json/experiment/first.results.json",
            "uploaders/uploader/data/json/experiment/first.log",
            "uploaders/uploader/data/json/experiment/first.transcript.pdf",
        }
    ]


def test_non_conflict_upload_error_is_not_retried(tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    class AuthenticationError(RuntimeError):
        response = SimpleNamespace(status_code=401)

    class FakeApi:
        def __init__(self):
            self.repo_info_calls = 0

        def repo_info(self, **kwargs):
            self.repo_info_calls += 1
            return SimpleNamespace(sha="remote-head", private=True)

        def create_commit(self, **kwargs):
            raise AuthenticationError("denied")

    api = FakeApi()
    with pytest.raises(AuthenticationError, match="denied"):
        hf_sync.sync_completed_runs(
            [final],
            repo_id="owner/dataset",
            namespace="uploader",
            data_root=data_root,
            lock_path=tmp_path / "sync.lock",
            api=api,
        )

    assert api.repo_info_calls == 1


def test_sync_refuses_public_dataset_by_default(tmp_path):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    class FakeApi:
        def repo_info(self, **kwargs):
            return SimpleNamespace(sha="remote-head", private=False)

        def create_commit(self, **kwargs):
            raise AssertionError("public dataset must not receive an upload")

    with pytest.raises(RuntimeError, match="refusing to upload to public dataset"):
        hf_sync.sync_completed_runs(
            [final],
            repo_id="owner/dataset",
            namespace="uploader",
            data_root=data_root,
            lock_path=tmp_path / "sync.lock",
            api=FakeApi(),
        )


def test_repo_env_loader_targets_project_dotenv(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(hf_sync, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr("dotenv.load_dotenv", lambda path: calls.append(path))

    hf_sync._load_repo_env()

    assert calls == [tmp_path / ".env"]


def test_automatic_hook_is_noop_unless_enabled(monkeypatch):
    called = []
    monkeypatch.setattr(
        hf_sync,
        "sync_completed_runs",
        lambda *args, **kwargs: called.append((args, kwargs)),
    )

    result = hf_sync.maybe_sync_completed_runs(
        [],
        environ={"HF_DATASET_REPO": "owner/dataset"},
    )

    assert result is False
    assert called == []


def test_automatic_hook_discovers_only_valid_finals_in_output_directory(
    monkeypatch,
    tmp_path,
):
    data_root = tmp_path / "data" / "json"
    run_dir = data_root / "experiment"
    final = write_json(run_dir / "run.json", FULL_STATE)
    write_json(run_dir / "run.results.json", FULL_STATE)
    write_json(run_dir / "run.checkpoint.json", FULL_STATE)
    write_json(run_dir / "run.checkpoint.json.error.json", FULL_STATE)
    write_json(run_dir / "analysis.json", {"metadata": {}, "trials": []})
    (run_dir / "truncated.json").write_text("{", encoding="utf-8")

    uploaded = []

    def capture(paths, **kwargs):
        uploaded.append((tuple(paths), kwargs))
        return SimpleNamespace(artifact_paths=(), final_paths=())

    monkeypatch.setattr(hf_sync, "DATA_JSON_ROOT", data_root)
    monkeypatch.setattr(hf_sync, "sync_completed_runs", capture)

    result = hf_sync.maybe_sync_completed_runs(
        [run_dir],
        environ={
            "HF_DATASET_AUTO_UPLOAD": "1",
            "HF_DATASET_REPO": "owner/dataset",
            "HF_DATASET_NAMESPACE": "uploader",
        },
    )

    assert result is True
    assert uploaded[0][0] == (final.resolve(),)


def test_automatic_hook_warns_and_swallows_upload_failure(monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise RuntimeError("authentication failed")

    monkeypatch.setattr(hf_sync, "sync_completed_runs", fail)

    result = hf_sync.maybe_sync_completed_runs(
        [],
        environ={
            "HF_DATASET_AUTO_UPLOAD": "1",
            "HF_DATASET_REPO": "owner/dataset",
            "HF_DATASET_NAMESPACE": "uploader",
        },
    )

    assert result is False
    assert "authentication failed" in capsys.readouterr().err


def test_dry_run_cli_needs_no_hugging_face_authentication(tmp_path, capsys):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    exit_status = hf_sync.main(
        [
            str(final),
            "--data-root",
            str(data_root),
            "--namespace",
            "uploader",
            "--dry-run",
        ]
    )

    output = capsys.readouterr().out
    assert exit_status == 0
    assert "completed_runs=1 artifacts=1" in output
    assert "uploaders/uploader/data/json/experiment/run.json" in output


def test_automatic_hook_requires_uploader_namespace(monkeypatch, capsys):
    monkeypatch.setattr(
        hf_sync,
        "sync_completed_runs",
        lambda *args, **kwargs: pytest.fail("sync must not be attempted"),
    )

    result = hf_sync.maybe_sync_completed_runs(
        [],
        environ={
            "HF_DATASET_AUTO_UPLOAD": "1",
            "HF_DATASET_REPO": "owner/dataset",
        },
    )

    assert result is False
    assert "HF_DATASET_NAMESPACE is unset" in capsys.readouterr().err


@pytest.mark.parametrize("namespace", ["", "../escape", "two/levels", "has space"])
def test_plan_rejects_unsafe_namespace(tmp_path, namespace):
    data_root = tmp_path / "data" / "json"
    final = write_json(data_root / "experiment" / "run.json", FULL_STATE)

    with pytest.raises(ValueError, match="HF_DATASET_NAMESPACE"):
        hf_sync.build_upload_plan(
            [final],
            repo_id="owner/dataset",
            namespace=namespace,
            data_root=data_root,
        )
