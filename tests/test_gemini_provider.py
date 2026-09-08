import json
import unittest
from unittest.mock import patch

from src.utils import (
    _call_gemini,
    _gemini_request_timeout_seconds,
    _gemini_supports_temperature,
)


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return json.dumps(
            {
                "candidates": [
                    {"content": {"parts": [{"text": '{"send": 5}'}]}}
                ],
                "usageMetadata": {
                    "promptTokenCount": 10,
                    "candidatesTokenCount": 4,
                    "thoughtsTokenCount": 2,
                },
            }
        ).encode("utf-8")


class GeminiProviderTests(unittest.TestCase):
    def setUp(self):
        self.client = {
            "api_key": "test-key",
            "base_url": "https://example.invalid/v1beta",
        }
        self.messages = [
            {"role": "system", "content": "Rules"},
            {"role": "user", "content": "Choose"},
        ]

    def _payload(self, mocked_urlopen):
        request = mocked_urlopen.call_args.args[0]
        return json.loads(request.data.decode("utf-8"))

    @patch("src.utils.urllib.request.urlopen", return_value=_FakeResponse())
    def test_gemini_37_omits_deprecated_temperature(self, mocked_urlopen):
        result = _call_gemini(
            self.client,
            "gemini-3.7-flash",
            0.8,
            self.messages,
            max_retries=1,
        )

        self.assertEqual(result["content"], '{"send": 5}')
        self.assertNotIn("temperature", self._payload(mocked_urlopen)["generationConfig"])
        self.assertFalse(_gemini_supports_temperature("gemini-3.7-flash"))

    @patch("src.utils.urllib.request.urlopen", return_value=_FakeResponse())
    def test_earlier_gemini_keeps_historical_temperature(self, mocked_urlopen):
        _call_gemini(
            self.client,
            "gemini-3.1-flash-lite",
            0.8,
            self.messages,
            max_retries=1,
        )

        self.assertEqual(
            self._payload(mocked_urlopen)["generationConfig"]["temperature"],
            0.8,
        )
        self.assertTrue(_gemini_supports_temperature("gemini-3.1-flash-lite"))

    @patch("src.utils.urllib.request.urlopen", return_value=_FakeResponse())
    def test_gemini_36_minimal_thinking_and_temperature(self, mocked_urlopen):
        # 3.6 Flash is the matched-reasoning Gemini arm: it accepts
        # thinking_level=minimal (3.7/3.8 stop at low). Like 3.7 it ignores
        # temperature (live probe 2026-09-04, scripts/probe_gemini_settings.py:
        # 5/5 distinct outputs at temperature 0), so the parameter is omitted
        # and run metadata records temperature_sent=false.
        with patch.dict("os.environ", {"GEMINI_THINKING_LEVEL": "minimal"}):
            _call_gemini(
                self.client,
                "gemini-3.6-flash",
                0.8,
                self.messages,
                max_retries=1,
            )

        config = self._payload(mocked_urlopen)["generationConfig"]
        self.assertNotIn("temperature", config)
        self.assertEqual(config["thinkingConfig"], {"thinkingLevel": "minimal"})
        self.assertFalse(_gemini_supports_temperature("gemini-3.6-flash"))

    def test_gemini_36_slug_resolves_to_direct_model_id(self):
        from src.utils import DIRECT_MODEL_ALIASES

        self.assertEqual(
            DIRECT_MODEL_ALIASES["google/gemini-3.6-flash"], "gemini-3.6-flash"
        )

    def test_timeout_defaults_and_validates_override(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(_gemini_request_timeout_seconds(), 120.0)
        with patch.dict(
            "os.environ", {"GEMINI_REQUEST_TIMEOUT_SECONDS": "300"}, clear=True
        ):
            self.assertEqual(_gemini_request_timeout_seconds(), 300.0)
        with patch.dict(
            "os.environ", {"GEMINI_REQUEST_TIMEOUT_SECONDS": "zero"}, clear=True
        ):
            with self.assertRaisesRegex(RuntimeError, "positive number"):
                _gemini_request_timeout_seconds()


if __name__ == "__main__":
    unittest.main()
