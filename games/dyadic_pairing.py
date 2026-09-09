import hashlib
import random
from collections import Counter, defaultdict


class DyadicPairingMixin:
    """Shared pairing/name helpers for games played in two-agent dyads."""

    requires_even_agents = True
    VALID_PAIRING_MODES = {"balanced", "fixed"}
    VALID_DEFECTOR_ACTION_POLICIES = {"prompted", "forced_zero"}
    # ``standard_substitute`` leaves defector myth generation untouched but,
    # when an ordinary agent would receive a defector-authored myth in the next
    # round, presents another ordinary author's myth from the same prior round.
    # The policy therefore manipulates cultural circulation without changing
    # defector game actions or the number of myth LLM calls.
    VALID_DEFECTOR_MYTH_POLICIES = {"normal", "standard_substitute"}

    def set_defector_options(
        self,
        defector_ratio=0.0,
        defector_agent_ids=None,
        defector_seed=0,
        defector_prompt_template=None,
        defector_action_policy="prompted",
        defector_myth_policy="normal",
        defector_role_visible_to_self=True,
        random_defection_probability=0.0,
        random_defection_seed=0,
    ):
        try:
            ratio = float(defector_ratio or 0.0)
        except (TypeError, ValueError) as exc:
            raise ValueError("defector_ratio must be a number between 0 and 1.") from exc
        if not 0 <= ratio <= 1:
            raise ValueError("defector_ratio must be between 0 and 1.")

        try:
            random_probability = float(random_defection_probability or 0.0)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "random_defection_probability must be a number between 0 and 1."
            ) from exc
        if not 0 <= random_probability <= 1:
            raise ValueError(
                "random_defection_probability must be between 0 and 1."
            )

        if defector_agent_ids is None:
            requested_ids = None
        elif isinstance(defector_agent_ids, str):
            requested_ids = [defector_agent_ids]
        else:
            requested_ids = list(defector_agent_ids)
        if requested_ids and len(set(requested_ids)) != len(requested_ids):
            raise ValueError("defector_agent_ids must not contain duplicates.")

        self.defector_ratio = ratio
        self.requested_defector_agent_ids = requested_ids
        self.defector_seed = 0 if defector_seed is None else defector_seed
        self.defector_prompt_template = defector_prompt_template
        self.defector_action_policy = self._validate_choice(
            "defector_action_policy",
            defector_action_policy,
            self.VALID_DEFECTOR_ACTION_POLICIES,
        )
        self.defector_myth_policy = self._validate_choice(
            "defector_myth_policy",
            defector_myth_policy,
            self.VALID_DEFECTOR_MYTH_POLICIES,
        )
        self.defector_role_visible_to_self = self._coerce_bool(
            defector_role_visible_to_self,
            True,
        )
        self.random_defection_probability = random_probability
        self.random_defection_seed = (
            0 if random_defection_seed is None else random_defection_seed
        )
        self.defector_agent_ids = []

    def _init_dyadic_agents(self):
        self.agent_ids = ["Agent_1", "Agent_2"]
        self.agent_names = {agent_id: agent_id for agent_id in self.agent_ids}
        if not hasattr(self, "pairing_mode"):
            self.pairing_mode = "balanced"
        if not hasattr(self, "pairing_seed"):
            self.set_pairing_seed(None)
        if not hasattr(self, "show_agent_names"):
            self.show_agent_names = True
        if not hasattr(self, "defector_ratio"):
            self.set_defector_options()
        self._round_pairings = {}
        self._balanced_pairing_schedule = {}
        self._sync_agent_aliases()

    def configure_agents(self, agent_ids, agent_names=None):
        if len(agent_ids) < 2:
            raise ValueError("Dyadic games require at least two agents.")
        if len(agent_ids) % 2 != 0:
            raise ValueError(
                f"Dyadic games require an even number of agents; got {len(agent_ids)}."
            )

        self.agent_ids = list(agent_ids)
        self.agent_names = {
            agent_id: str((agent_names or {}).get(agent_id, agent_id))
            for agent_id in self.agent_ids
        }
        if len(set(self.agent_names.values())) != len(self.agent_names):
            raise ValueError("Agent display names must be unique.")

        self._assign_defectors()
        self._round_pairings = {}
        self._balanced_pairing_schedule = {}
        self._sync_agent_aliases()

    def _assign_defectors(self):
        if self.requested_defector_agent_ids is not None:
            unknown_ids = sorted(set(self.requested_defector_agent_ids) - set(self.agent_ids))
            if unknown_ids:
                raise ValueError(
                    "Unknown defector_agent_ids: " + ", ".join(unknown_ids)
                )
            selected = list(self.requested_defector_agent_ids)
        else:
            target_count = int(len(self.agent_ids) * self.defector_ratio + 0.5)
            if self.defector_ratio > 0 and target_count == 0:
                target_count = 1
            target_count = min(len(self.agent_ids), target_count)
            selected = random.Random(self.defector_seed).sample(
                self.agent_ids,
                target_count,
            )

        selected_ids = set(selected)
        self.defector_agent_ids = [
            agent_id for agent_id in self.agent_ids if agent_id in selected_ids
        ]
        if self._defector_prompt_is_required() and not self.defector_prompt_template:
            raise ValueError(
                "A defector_prompt_template is required when defectors are configured."
            )

    def restore_defector_agent_ids(self, agent_ids):
        """Restore a saved assignment when resuming a run."""
        restored = list(agent_ids or [])
        unknown_ids = sorted(set(restored) - set(self.agent_ids))
        if unknown_ids:
            raise ValueError(
                "Saved defector_agent_ids are not in the current population: "
                + ", ".join(unknown_ids)
            )
        if (
            self._defector_prompt_is_required(restored)
            and not self.defector_prompt_template
        ):
            raise ValueError(
                "A defector_prompt_template is required when restoring defectors."
            )
        restored_ids = set(restored)
        self.defector_agent_ids = [
            agent_id for agent_id in self.agent_ids if agent_id in restored_ids
        ]

    def is_defector(self, agent_id):
        return agent_id in self.defector_agent_ids

    def _validate_choice(self, name, value, valid_values):
        normalized = str(value or "").strip().lower()
        if normalized not in valid_values:
            choices = ", ".join(sorted(valid_values))
            raise ValueError(f"{name} must be one of: {choices}; got {value!r}")
        return normalized

    def _defector_prompt_is_required(self, agent_ids=None):
        configured_ids = (
            self.defector_agent_ids if agent_ids is None else agent_ids
        )
        return bool(configured_ids) and (
            self.defector_action_policy == "prompted"
            or self.defector_role_visible_to_self
        )

    def is_random_defection(self, agent_id, role, turn):
        """Return whether this standard-agent decision is a seeded defection.

        The schedule is keyed by replicate seed, round, agent, and role rather
        than mutable RNG state. It is therefore stable across retries/resumes,
        shared across model/task-order cells, and nested across probabilities:
        every event in a 25% arm also occurs in its matched 50% arm.
        """
        if self.random_defection_probability <= 0 or self.is_defector(agent_id):
            return False
        if turn is None:
            raise ValueError(
                "turn is required when random_defection_probability is positive."
            )
        if role not in {"investor", "trustee"}:
            raise ValueError(f"Unknown trust-game role for {agent_id}: {role!r}")

        key = (
            "random-defection-v1|"
            f"{self.random_defection_seed}|{int(turn)}|{agent_id}|{role}"
        ).encode("utf-8")
        draw = int.from_bytes(hashlib.sha256(key).digest()[:8], "big") / 2**64
        return draw < self.random_defection_probability

    def get_forced_game_response(self, agent_id, role, turn=None):
        """Return a deterministic zero response for a configured defection."""
        response_source = None
        if self.is_defector(agent_id):
            if self.defector_action_policy != "forced_zero":
                return None
            response_source = "forced_zero"
        elif self.is_random_defection(agent_id, role, turn):
            response_source = "random_defection_forced_zero"
        else:
            return None

        if role == "investor":
            content = '{"send": 0}'
        elif role == "trustee":
            content = '{"return": 0}'
        else:
            raise ValueError(f"Unknown trust-game role for {agent_id}: {role!r}")
        return {
            "content": content,
            "reasoning": None,
            "usage": None,
            "response_source": response_source,
        }

    def get_agent_types(self):
        return {
            agent_id: "defector" if self.is_defector(agent_id) else "standard"
            for agent_id in self.agent_ids
        }

    def get_population_metadata(self):
        defector_count = len(self.defector_agent_ids)
        population_size = len(self.agent_ids)
        return {
            "defector_ratio_requested": self.defector_ratio,
            "defector_ratio_actual": (
                defector_count / population_size if population_size else 0.0
            ),
            "defector_count": defector_count,
            "defector_agent_ids": list(self.defector_agent_ids),
            "defector_seed": self.defector_seed,
            "defector_action_policy": self.defector_action_policy,
            "defector_myth_policy": self.defector_myth_policy,
            "defector_role_visible_to_self": self.defector_role_visible_to_self,
            "random_defection_probability": self.random_defection_probability,
            "random_defection_seed": self.random_defection_seed,
            "random_defection_unit": "agent_game_decision",
            "agent_types": self.get_agent_types(),
        }

    def _sync_agent_aliases(self):
        self.agent_1_id = self.agent_ids[0] if self.agent_ids else "Agent_1"
        self.agent_2_id = self.agent_ids[1] if len(self.agent_ids) > 1 else "Agent_2"

    def set_pairing_mode(self, pairing_mode="balanced"):
        normalized = str(pairing_mode or "balanced").strip().lower()
        if normalized not in self.VALID_PAIRING_MODES:
            choices = ", ".join(sorted(self.VALID_PAIRING_MODES))
            raise ValueError(
                f"pairing_mode must be one of: {choices}; got {pairing_mode!r}"
            )
        self.pairing_mode = normalized

    def set_pairing_seed(self, pairing_seed=None):
        self.pairing_seed = pairing_seed
        self._pairing_rng = (
            random if pairing_seed is None else random.Random(pairing_seed)
        )

    def get_agent_display_name(self, agent_id):
        return self.agent_names.get(agent_id, agent_id)

    def _coerce_bool(self, value, default=True):
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
        return default

    def set_prompt_name_visibility(self, show_agent_names=True):
        self.show_agent_names = self._coerce_bool(show_agent_names, True)

    def names_visible_in_prompts(self):
        return self._coerce_bool(getattr(self, "show_agent_names", True), True)

    def current_coplayer_label(self, agent_id):
        if self.names_visible_in_prompts():
            return self.get_agent_display_name(agent_id)
        return "your current co-player"

    def public_ledger_label(self, agent_id):
        """Return a stable neutral pseudonym without revealing display names."""
        try:
            index = self.agent_ids.index(agent_id)
        except ValueError as exc:
            raise ValueError(f"Unknown agent ID for public ledger: {agent_id!r}") from exc

        # Spreadsheet-style labels keep this deterministic beyond 26 agents.
        letters = ""
        value = index + 1
        while value:
            value, remainder = divmod(value - 1, 26)
            letters = chr(ord("A") + remainder) + letters
        return f"Member {letters}"

    def self_prompt_label(self, agent_id):
        if self.names_visible_in_prompts():
            return self.get_agent_display_name(agent_id)
        return "you"

    def role_prompt_label(self, agent_id, role):
        if self.names_visible_in_prompts():
            return self.get_agent_display_name(agent_id)
        return "the sender" if role == "investor" else "the receiver"

    def history_coplayer_label(
        self,
        agent_id,
        observer_agent_id=None,
        current_coplayer_id=None,
    ):
        if self.names_visible_in_prompts():
            return self.get_agent_display_name(agent_id)
        if observer_agent_id and agent_id == observer_agent_id:
            return "you"
        if current_coplayer_id and agent_id == current_coplayer_id:
            return "your current co-player"
        return "another agent"

    def coplayer_history_heading(self, agent_id):
        if self.names_visible_in_prompts():
            return f"{self.get_agent_display_name(agent_id)}'s"
        return "Your current co-player's"

    def get_round_pairings(self, turn, sim_data=None):
        if turn in self._round_pairings:
            return self._round_pairings[turn]

        existing = self._get_existing_pairings(turn, sim_data)
        if existing:
            self._round_pairings[turn] = existing
            return existing

        if len(self.agent_ids) == 2:
            if turn % 2 == 1:
                raw_pairs = [(self.agent_1_id, self.agent_2_id)]
            else:
                raw_pairs = [(self.agent_2_id, self.agent_1_id)]
        elif sim_data is not None:
            if getattr(self, "pairing_mode", "balanced") == "fixed":
                pairings = self._get_fixed_multi_agent_pairings(turn)
            else:
                pairings = self._get_balanced_multi_agent_pairings(turn, sim_data)
            self._round_pairings[turn] = pairings
            return pairings
        else:
            raw_pairs = self._random_multi_agent_pairs()

        pairings = []
        for idx, (investor_id, trustee_id) in enumerate(raw_pairs, start=1):
            pairings.append(self._pairing_record(turn, idx, investor_id, trustee_id))

        self._round_pairings[turn] = pairings
        return pairings

    def _get_balanced_multi_agent_pairings(self, turn, sim_data):
        total_rounds = self._get_total_rounds(turn, sim_data)
        schedule = self._get_or_create_balanced_pairing_schedule(total_rounds, sim_data)
        scheduled = schedule.get(str(turn))
        if scheduled is None:
            scheduled = self._build_balanced_remaining_schedule(
                total_rounds,
                sim_data,
            ).get(str(turn))
        if scheduled is None:
            raw_pairs = self._random_multi_agent_pairs()
            return [
                self._pairing_record(turn, idx, investor_id, trustee_id)
                for idx, (investor_id, trustee_id) in enumerate(raw_pairs, start=1)
            ]
        return [
            self._normalize_pairing(turn, idx, pairing)
            for idx, pairing in enumerate(scheduled, start=1)
        ]

    def _get_fixed_multi_agent_pairings(self, turn):
        """Keep each adjacent agent pair together and swap roles by parity."""
        base_pairs = [
            (self.agent_ids[index], self.agent_ids[index + 1])
            for index in range(0, len(self.agent_ids), 2)
        ]
        pairings = []
        for idx, (first, second) in enumerate(base_pairs, start=1):
            if turn % 2 == 1:
                investor_id, trustee_id = first, second
            else:
                investor_id, trustee_id = second, first
            pairings.append(
                self._pairing_record(turn, idx, investor_id, trustee_id)
            )
        return pairings

    def _get_total_rounds(self, turn, sim_data):
        metadata = getattr(sim_data, "run_metadata", {}) or {}
        try:
            return max(turn, int(metadata.get("num_turns") or turn))
        except (TypeError, ValueError):
            return turn

    def _get_or_create_balanced_pairing_schedule(self, total_rounds, sim_data):
        game_data = getattr(sim_data, "game_data", {}) or {}
        schedule_data = game_data.get("dyadic_pairing_schedule") or {}
        if self._schedule_data_matches(schedule_data, total_rounds):
            self._balanced_pairing_schedule = schedule_data.get("rounds", {})
            return self._balanced_pairing_schedule

        role_targets = self._role_targets_for_schedule(total_rounds, sim_data)
        schedule = self._build_balanced_remaining_schedule(
            total_rounds,
            sim_data,
            role_targets,
        )
        game_data["dyadic_pairing_schedule"] = {
            "strategy": "balanced_random_roles_v1",
            "num_turns": total_rounds,
            "agent_ids": list(self.agent_ids),
            "role_targets": role_targets,
            "rounds": schedule,
        }
        self._balanced_pairing_schedule = schedule
        return schedule

    def _schedule_data_matches(self, schedule_data, total_rounds):
        return (
            schedule_data.get("strategy") == "balanced_random_roles_v1"
            and schedule_data.get("num_turns") == total_rounds
            and schedule_data.get("agent_ids") == list(self.agent_ids)
            and isinstance(schedule_data.get("rounds"), dict)
        )

    def _build_balanced_remaining_schedule(self, total_rounds, sim_data, role_targets=None):
        existing_by_turn = self._existing_pairings_by_turn(sim_data)
        role_targets = role_targets or self._role_targets_for_schedule(total_rounds, sim_data)
        sender_counts = Counter()
        partner_counts = defaultdict(int)
        schedule = {}

        for round_number in range(1, total_rounds + 1):
            existing = existing_by_turn.get(round_number)
            if existing:
                pairings = [
                    self._normalize_pairing(round_number, idx, pairing)
                    for idx, pairing in enumerate(existing, start=1)
                ]
            else:
                pairings = self._build_balanced_round_pairings(
                    round_number,
                    role_targets,
                    sender_counts,
                    partner_counts,
                )

            schedule[str(round_number)] = pairings
            self._accumulate_pairing_counts(pairings, sender_counts, partner_counts)

        return schedule

    def _role_targets_for_schedule(self, total_rounds, sim_data):
        existing_sender_counts = Counter()
        for pairings in self._existing_pairings_by_turn(sim_data).values():
            for pairing in pairings:
                investor_id = pairing.get("investor")
                if investor_id in self.agent_ids:
                    existing_sender_counts[investor_id] += 1

        total_sender_slots = total_rounds * (len(self.agent_ids) // 2)
        targets = {agent_id: existing_sender_counts[agent_id] for agent_id in self.agent_ids}

        while sum(targets.values()) < total_sender_slots:
            min_count = min(targets.values())
            candidates = [agent_id for agent_id, count in targets.items() if count == min_count]
            targets[self._pairing_rng.choice(candidates)] += 1

        return targets

    def _existing_pairings_by_turn(self, sim_data):
        existing_by_turn = {}
        if sim_data is None:
            return existing_by_turn

        for entry in getattr(sim_data, "conversation_history", []) or []:
            try:
                turn = int(entry.get("round"))
            except (TypeError, ValueError):
                continue
            pairings = entry.get("pairings")
            if pairings:
                existing_by_turn[turn] = [
                    self._normalize_pairing(turn, idx, pairing)
                    for idx, pairing in enumerate(pairings, start=1)
                ]
                continue

            dyads = entry.get("dyads")
            if dyads:
                existing_by_turn[turn] = [
                    self._normalize_pairing(turn, idx, dyad)
                    for idx, dyad in enumerate(dyads, start=1)
                ]
                continue

            roles = entry.get("roles") or {}
            investor_id = next((aid for aid, role in roles.items() if role == "investor"), None)
            trustee_id = next((aid for aid, role in roles.items() if role == "trustee"), None)
            if investor_id and trustee_id:
                existing_by_turn[turn] = [self._pairing_record(turn, 1, investor_id, trustee_id)]

        return existing_by_turn

    def _build_balanced_round_pairings(
        self,
        turn,
        role_targets,
        sender_counts,
        partner_counts,
    ):
        sender_slots = len(self.agent_ids) // 2
        remaining_sender_need = {
            agent_id: role_targets.get(agent_id, 0) - sender_counts[agent_id]
            for agent_id in self.agent_ids
        }
        shuffled_agents = list(self.agent_ids)
        self._pairing_rng.shuffle(shuffled_agents)
        senders = sorted(
            shuffled_agents,
            key=lambda agent_id: remaining_sender_need[agent_id],
            reverse=True,
        )[:sender_slots]
        receivers = [agent_id for agent_id in self.agent_ids if agent_id not in set(senders)]

        self._pairing_rng.shuffle(senders)
        self._pairing_rng.shuffle(receivers)
        pairs = []
        available_receivers = set(receivers)
        for sender in senders:
            best_receivers = self._least_repeated_receivers(
                sender,
                available_receivers,
                partner_counts,
            )
            receiver = self._pairing_rng.choice(best_receivers)
            available_receivers.remove(receiver)
            pairs.append((sender, receiver))

        self._pairing_rng.shuffle(pairs)
        return [
            self._pairing_record(turn, idx, investor_id, trustee_id)
            for idx, (investor_id, trustee_id) in enumerate(pairs, start=1)
        ]

    def _least_repeated_receivers(self, sender, available_receivers, partner_counts):
        min_count = min(
            partner_counts[frozenset((sender, receiver))]
            for receiver in available_receivers
        )
        # ``available_receivers`` is a set. Its iteration order depends on
        # Python's process-level hash seed, so feeding that order directly to
        # Random.choice makes a recorded pairing seed non-reproducible across
        # separate interpreter processes. Canonicalize the candidates before
        # the seeded choice is made.
        return sorted(
            receiver
            for receiver in available_receivers
            if partner_counts[frozenset((sender, receiver))] == min_count
        )

    def _accumulate_pairing_counts(self, pairings, sender_counts, partner_counts):
        for pairing in pairings:
            investor_id = pairing.get("investor")
            trustee_id = pairing.get("trustee")
            if investor_id in self.agent_ids:
                sender_counts[investor_id] += 1
            if investor_id in self.agent_ids and trustee_id in self.agent_ids:
                partner_counts[frozenset((investor_id, trustee_id))] += 1

    def _random_multi_agent_pairs(self):
        shuffled = list(self.agent_ids)
        self._pairing_rng.shuffle(shuffled)

        raw_pairs = []
        for idx in range(0, len(shuffled), 2):
            pair = shuffled[idx:idx + 2]
            self._pairing_rng.shuffle(pair)
            raw_pairs.append(tuple(pair))
        return raw_pairs

    def _get_existing_pairings(self, turn, sim_data):
        if sim_data is None:
            return None
        for entry in sim_data.conversation_history:
            if entry.get("round") != turn:
                continue
            pairings = entry.get("pairings")
            if pairings:
                return [self._normalize_pairing(turn, idx, p) for idx, p in enumerate(pairings, start=1)]
            dyads = entry.get("dyads")
            if dyads:
                return [self._normalize_pairing(turn, idx, d) for idx, d in enumerate(dyads, start=1)]
            roles = entry.get("roles") or {}
            investor_id = next((aid for aid, role in roles.items() if role == "investor"), None)
            trustee_id = next((aid for aid, role in roles.items() if role == "trustee"), None)
            if investor_id and trustee_id:
                return [self._pairing_record(turn, 1, investor_id, trustee_id)]
        return None

    def _normalize_pairing(self, turn, idx, pairing):
        investor_id = pairing.get("investor")
        trustee_id = pairing.get("trustee")
        if not investor_id or not trustee_id:
            agents = pairing.get("agents") or []
            roles = pairing.get("roles") or {}
            investor_id = investor_id or next(
                (aid for aid in agents if roles.get(aid) == "investor"), None
            )
            trustee_id = trustee_id or next(
                (aid for aid in agents if roles.get(aid) == "trustee"), None
            )
        return self._pairing_record(
            turn,
            idx,
            investor_id,
            trustee_id,
            dyad_id=pairing.get("dyad_id"),
        )

    def _pairing_record(self, turn, idx, investor_id, trustee_id, dyad_id=None):
        dyad_id = dyad_id or f"dyad_{idx}"
        agents = [investor_id, trustee_id]
        return {
            "round": turn,
            "dyad_id": dyad_id,
            "agents": agents,
            "investor": investor_id,
            "trustee": trustee_id,
            "roles": {
                investor_id: "investor",
                trustee_id: "trustee",
            },
            "agent_names": {
                agent_id: self.get_agent_display_name(agent_id)
                for agent_id in agents
            },
        }

    def get_roles_for_round(self, turn, sim_data=None):
        pairings = self.get_round_pairings(turn, sim_data)
        if len(pairings) == 1:
            return {
                "investor": pairings[0]["investor"],
                "trustee": pairings[0]["trustee"],
            }
        return self.get_roles_by_agent_for_round(turn, sim_data)

    def get_roles_by_agent_for_round(self, turn, sim_data=None):
        roles = {}
        for pairing in self.get_round_pairings(turn, sim_data):
            roles.update(pairing["roles"])
        return roles

    def get_move_order(self, turn, sim_data):
        move_order = []
        for pairing in self.get_round_pairings(turn, sim_data):
            move_order.extend([pairing["investor"], pairing["trustee"]])
        return move_order

    def get_pairing_for_agent(self, agent_id, turn, sim_data=None):
        for pairing in self.get_round_pairings(turn, sim_data):
            if agent_id in pairing["agents"]:
                return pairing
        raise ValueError(f"No pairing found for {agent_id} in round {turn}.")

    def get_pairing_by_dyad_id(self, dyad_id, turn, sim_data=None):
        for pairing in self.get_round_pairings(turn, sim_data):
            if pairing["dyad_id"] == dyad_id:
                return pairing
        raise ValueError(f"No dyad {dyad_id} found in round {turn}.")

    def get_opponent_id(self, agent_id, turn, sim_data=None):
        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        return pairing["trustee"] if agent_id == pairing["investor"] else pairing["investor"]

    def with_prompt_context(self, prompt, agent_id, opponent_id=None):
        contextualized_prompt = prompt
        unified_prompts = getattr(self, "prompt_regime", "legacy") == "unified"
        if (
            (len(self.agent_ids) > 2 or unified_prompts)
            and self.names_visible_in_prompts()
        ):
            lines = [
                f"Your name in this experiment is {self.get_agent_display_name(agent_id)}."
            ]
            if opponent_id:
                lines.append(
                    "Your opponent this round is "
                    f"{self.get_agent_display_name(opponent_id)} ({opponent_id})."
                )
            contextualized_prompt = "\n".join(lines) + "\n\n" + prompt

        if self.is_defector(agent_id) and (
            self.defector_action_policy == "prompted"
            or self.defector_role_visible_to_self
        ):
            contextualized_prompt = (
                contextualized_prompt.rstrip()
                + "\n\n"
                + self.defector_prompt_template.strip()
                + "\n"
            )
        return contextualized_prompt

    def with_system_context(self, prompt, agent_id):
        unified_prompts = getattr(self, "prompt_regime", "legacy") == "unified"
        if len(self.agent_ids) <= 2 and not unified_prompts:
            return prompt

        effective_pairing_mode = (
            "fixed"
            if len(self.agent_ids) == 2
            else getattr(self, "pairing_mode", "balanced")
        )
        if not unified_prompts and effective_pairing_mode == "balanced":
            return (
                prompt
                + "\n\nMULTI-AGENT SETTING:\n"
                + f"- There are {len(self.agent_ids)} agents in this run.\n"
                + "- Each round, all agents are paired into dyads from the full pool. Pairings are randomized, but the schedule balances sender and receiver roles across the run.\n"
                + "- You play one sender-receiver game with your paired opponent each round.\n"
                + "- Your role may repeat across consecutive rounds, but by the end of the run every agent will have acted as sender and receiver equally often when the round count allows it.\n"
                + self._system_name_context(agent_id)
            )

        lines = [
            "POPULATION SETTING:",
            f"- There are {len(self.agent_ids)} agents in this run.",
        ]
        if effective_pairing_mode == "fixed":
            lines.extend(
                [
                    "- You remain paired with the same opponent throughout the run.",
                    "- You play one sender-receiver game with that opponent each round.",
                    "- Sender and receiver roles alternate every round.",
                ]
            )
        else:
            lines.extend(
                [
                    "- Each round, all agents are paired into dyads from the full pool. Pairings are randomized, but the schedule balances sender and receiver roles across the run.",
                    "- You play one sender-receiver game with your paired opponent each round.",
                    "- Your role may repeat across consecutive rounds, but by the end of the run every agent will have acted as sender and receiver equally often when the round count allows it.",
                ]
            )
        lines.append(self._system_name_context(agent_id))
        return prompt + "\n\n" + "\n".join(lines)

    def _system_name_context(self, agent_id):
        if self.names_visible_in_prompts():
            return (
                "- You will be told your opponent's name in each round.\n"
                + f"- Your name in this experiment is {self.get_agent_display_name(agent_id)}."
            )
        return (
            "- Agent names are hidden in this run.\n"
            "- Your paired opponent is referred to as your current co-player."
        )

    def iter_completed_dyads(self, entry):
        dyads = entry.get("dyads") or []
        if dyads:
            for dyad in dyads:
                if dyad.get("sent") is not None and dyad.get("returned") is not None:
                    yield dyad
            return

        roles = entry.get("roles") or {}
        investor_id = next((aid for aid, role in roles.items() if role == "investor"), None)
        trustee_id = next((aid for aid, role in roles.items() if role == "trustee"), None)
        if investor_id and trustee_id and entry.get("sent") is not None and entry.get("returned") is not None:
            yield {
                "round": entry.get("round"),
                "dyad_id": "dyad_1",
                "agents": [investor_id, trustee_id],
                "investor": investor_id,
                "trustee": trustee_id,
                "roles": roles,
                "sent": entry.get("sent"),
                "received": entry.get("received"),
                "returned": entry.get("returned"),
                "investor_payoff": entry.get("investor_payoff"),
                "trustee_payoff": entry.get("trustee_payoff"),
                "payoffs": {
                    investor_id: entry.get("investor_payoff"),
                    trustee_id: entry.get("trustee_payoff"),
                },
                "balances": entry.get("balances"),
                "actions": entry.get("actions"),
            }

    def find_last_completed_dyad_for_agent(self, agent_id, turn, sim_data):
        for entry in reversed(sim_data.conversation_history):
            try:
                entry_round = int(entry.get("round", 0))
            except (TypeError, ValueError):
                continue
            if entry_round >= turn:
                continue
            for dyad in self.iter_completed_dyads(entry):
                if agent_id in (dyad.get("agents") or []):
                    return dyad
        return None

    def find_completed_dyads_for_agent(self, agent_id, turn, sim_data, limit=None):
        dyads = []
        for entry in getattr(sim_data, "conversation_history", []) or []:
            try:
                entry_round = int(entry.get("round", 0))
            except (TypeError, ValueError):
                continue
            if entry_round >= turn:
                continue
            for dyad in self.iter_completed_dyads(entry):
                if agent_id not in (dyad.get("agents") or []):
                    continue
                dyad_with_round = dict(dyad)
                dyad_with_round.setdefault("round", entry_round)
                dyads.append(dyad_with_round)

        if limit is None:
            return dyads
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return dyads
        if limit <= 0:
            return []
        return dyads[-limit:]

    def get_opponent_from_dyad(self, dyad, agent_id):
        agents = dyad.get("agents") or []
        for other_agent_id in agents:
            if other_agent_id != agent_id:
                return other_agent_id
        return None
