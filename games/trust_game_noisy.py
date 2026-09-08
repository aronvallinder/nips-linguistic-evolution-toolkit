import glob
import hashlib
import json
import os
import random
import re

from games.base_game import Game
from games.dyadic_pairing import DyadicPairingMixin
from src.control_text_pool import get_filler_text
from src.shared_context import build_previous_round_shared_context


VALID_MYTH_INJECTION_MODES = {"partner", "own", "shuffled", "filler"}
VALID_NOISE_SEMANTICS = {"communication", "environmental"}


OTHER_PLAYER_NAMES = {
    "default": {"investor": "The sender", "trustee": "the receiver"},
    "prosocial": {"investor": "Prometheus", "trustee": "Orpheus"},
    "trickster": {"investor": "Coyote", "trustee": "Anansi"},
    "exchange": {"investor": "Persephone", "trustee": "Yggdrasil"},
    "neutral_myth": {"investor": "The Wanderer", "trustee": "The Guardian"},
}


class TrustGameNoisy(DyadicPairingMixin, Game):
    """Trust/Investment game with amount noise and optional asymmetric naming."""

    VALID_HISTORY_POLICIES = {
        "none",
        "minimal",
        "self_and_coplayer",
        "population_ledger",
        "stable_ids",
        "anonymous_population_record",
        "relative_pair_ids",
    }
    VALID_PROMPT_REGIMES = {"legacy", "unified"}
    VALID_PUNISHMENT_PROMPT_VARIANTS = {"current", "cost_salient"}

    def __init__(
        self,
        endowment,
        multiplier,
        system_prompt_template=None,
        personas=None,
        round1_investor_template=None,
        round1_trustee_template=None,
        later_investor_template=None,
        later_trustee_template=None,
        noise_config=None,
        noise_semantics="communication",
        other_player_names="default",
        myth_injection_mode="partner",
        shuffled_myth_pool_path=None,
        run_seed=None,
        history_policy="minimal",
        self_history_window=1,
        coplayer_history_window=0,
        population_history_window=0,
        show_agent_names=True,
        defector_ratio=0.0,
        defector_agent_ids=None,
        defector_seed=0,
        defector_prompt_template=None,
        defector_action_policy="prompted",
        defector_myth_policy="normal",
        defector_role_visible_to_self=True,
        random_defection_probability=0.0,
        random_defection_seed=0,
        game_prompt_addition="",
        pairing_mode="balanced",
        pairing_seed=None,
        noise_seed=None,
        prompt_regime="legacy",
        punishment_enabled=False,
        punishment_budget=2,
        punishment_effect_multiplier=3,
        punishment_prompt_variant="current",
    ):
        super().__init__()
        self.set_pairing_mode(pairing_mode)
        self.set_pairing_seed(pairing_seed)
        self.noise_seed = noise_seed
        self.prompt_regime = self._validate_prompt_regime(prompt_regime)
        self.endowment = endowment
        self.multiplier = multiplier
        self.system_prompt_template = system_prompt_template
        self.round1_investor_template = round1_investor_template
        self.round1_trustee_template = round1_trustee_template
        self.later_investor_template = later_investor_template
        self.later_trustee_template = later_trustee_template
        self.personas = personas or {}
        self.noise_config = noise_config or {}
        normalized_noise_semantics = str(
            noise_semantics or "communication"
        ).strip().lower()
        if normalized_noise_semantics not in VALID_NOISE_SEMANTICS:
            choices = ", ".join(sorted(VALID_NOISE_SEMANTICS))
            raise ValueError(
                f"noise_semantics must be one of: {choices}; "
                f"got {noise_semantics!r}"
            )
        self.noise_semantics = normalized_noise_semantics
        normalized_injection_mode = str(myth_injection_mode or "partner").strip().lower()
        if normalized_injection_mode not in VALID_MYTH_INJECTION_MODES:
            choices = ", ".join(sorted(VALID_MYTH_INJECTION_MODES))
            raise ValueError(
                f"myth_injection_mode must be one of: {choices}; "
                f"got {myth_injection_mode!r}"
            )
        self.myth_injection_mode = normalized_injection_mode
        self.shuffled_myth_pool_path = shuffled_myth_pool_path
        self.run_seed = run_seed
        self._shuffled_myth_pool = None
        if self.myth_injection_mode == "shuffled":
            self._shuffled_myth_pool = self._load_shuffled_myth_pool(
                shuffled_myth_pool_path
            )
        self.history_policy = self._validate_history_policy(history_policy)
        self.self_history_window = self._coerce_history_window(self_history_window, 1)
        self.coplayer_history_window = self._coerce_history_window(coplayer_history_window, 0)
        self.population_history_window = self._coerce_history_window(
            population_history_window,
            0,
        )
        if (
            self.history_policy
            in {"population_ledger", "anonymous_population_record"}
            and self.population_history_window <= 0
        ):
            raise ValueError(
                "population_history_window must be positive when "
                f"history_policy={self.history_policy!r}."
            )
        self.game_prompt_addition = (game_prompt_addition or "").strip()
        self.punishment_enabled = bool(punishment_enabled)
        self.punishment_budget = self._validate_nonnegative_integer(
            "punishment_budget",
            punishment_budget,
        )
        self.punishment_effect_multiplier = self._validate_positive_number(
            "punishment_effect_multiplier",
            punishment_effect_multiplier,
        )
        self.punishment_prompt_variant = self._validate_punishment_prompt_variant(
            punishment_prompt_variant
        )
        self.set_prompt_name_visibility(show_agent_names)
        self.set_defector_options(
            defector_ratio=defector_ratio,
            defector_agent_ids=defector_agent_ids,
            defector_seed=defector_seed,
            defector_prompt_template=defector_prompt_template,
            defector_action_policy=defector_action_policy,
            defector_myth_policy=defector_myth_policy,
            defector_role_visible_to_self=defector_role_visible_to_self,
            random_defection_probability=random_defection_probability,
            random_defection_seed=random_defection_seed,
        )

        if isinstance(other_player_names, str):
            self.other_player_names = OTHER_PLAYER_NAMES.get(
                other_player_names, OTHER_PLAYER_NAMES["default"]
            )
        else:
            self.other_player_names = other_player_names

        self._init_dyadic_agents()

    @staticmethod
    def _validate_nonnegative_integer(name, value):
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a non-negative integer.")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a non-negative integer.") from exc
        if numeric < 0 or not numeric.is_integer():
            raise ValueError(f"{name} must be a non-negative integer.")
        return int(numeric)

    @staticmethod
    def _validate_positive_number(name, value):
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a positive number.")
        try:
            numeric = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a positive number.") from exc
        if numeric <= 0:
            raise ValueError(f"{name} must be a positive number.")
        return numeric

    @staticmethod
    def _load_shuffled_myth_pool(pool_path):
        """Load myths used by the legacy shuffled-partner-text control."""
        if not pool_path:
            raise ValueError(
                "myth_injection_mode='shuffled' requires "
                "shuffled_myth_pool_path."
            )

        candidates = []
        if os.path.isdir(pool_path):
            for root, _directories, filenames in os.walk(pool_path):
                for filename in filenames:
                    if filename.endswith(".json"):
                        candidates.append(os.path.join(root, filename))
        else:
            candidates.extend(glob.glob(pool_path, recursive=True))

        pool = []
        ignored_suffixes = (".checkpoint.json", ".results.json", ".error.json")
        for candidate in sorted(candidates):
            if not candidate.endswith(".json") or candidate.endswith(ignored_suffixes):
                continue
            try:
                with open(candidate, encoding="utf-8") as handle:
                    payload = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            for entry in payload.get("conversation_history", []) or []:
                for myth in (entry.get("myths") or {}).values():
                    if isinstance(myth, str) and myth.strip():
                        pool.append(myth.strip())

        if not pool:
            raise ValueError(
                f"Shuffled myth pool at {pool_path!r} is empty. Check the path "
                "and that the runs contain non-empty myths."
            )
        return tuple(pool)

    def _make_myth_injection_seed_key(self, agent_id, sim_data, turn):
        parts = [
            str(self.run_seed) if self.run_seed is not None else "no_seed",
            agent_id,
            str(turn),
        ]
        task_order = getattr(sim_data, "task_order", None) if sim_data else None
        if task_order:
            parts.append("_".join(task_order))
        return "|".join(parts)

    @staticmethod
    def _latest_myth_for(target_agent_id, sim_data):
        if sim_data is None:
            return ""
        for entry in reversed(sim_data.conversation_history):
            myth = (entry.get("myths") or {}).get(target_agent_id)
            if isinstance(myth, str) and myth.strip():
                return myth.strip()
        return ""

    def _legacy_injected_myth(self, agent_id, opponent_id, sim_data, turn):
        """Resolve text for legacy partner/own/shuffled/filler prompt cells.

        Current corrected protocols use templates without the corresponding
        placeholder, so retaining this compatibility path cannot alter them.
        """
        if self.myth_injection_mode == "partner":
            return self._latest_myth_for(opponent_id, sim_data)
        if self.myth_injection_mode == "own":
            return self._latest_myth_for(agent_id, sim_data)

        seed_key = self._make_myth_injection_seed_key(agent_id, sim_data, turn)
        if self.myth_injection_mode == "filler":
            return get_filler_text(seed_key)
        if self.myth_injection_mode == "shuffled":
            digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % len(self._shuffled_myth_pool)
            return self._shuffled_myth_pool[index]
        return ""

    def _legacy_prompt_context(self, agent_id, opponent_id, sim_data, turn):
        injected_myth = self._legacy_injected_myth(
            agent_id,
            opponent_id,
            sim_data,
            turn,
        )
        myth_block = ""
        if injected_myth:
            myth_block = (
                "Your partner's most recent story:\n"
                f'"{injected_myth}"\n\n'
            )
        return {
            "other_agent_last_myth": injected_myth,
            "other_agent_last_myth_block": myth_block,
            "shared_context_block": build_previous_round_shared_context(
                agent_id,
                sim_data,
                turn,
            ),
        }

    def _apply_noise(self, actual_amount, max_amount, rng=None):
        if not self.noise_config:
            return actual_amount, actual_amount

        rng = rng or random
        noise_type = self.noise_config.get("type", "none")
        if noise_type == "uniform":
            noise_range = self.noise_config.get("range", 0)
            direction = self.noise_config.get("direction", "both")
            if direction == "negative":
                noise = rng.uniform(-noise_range, 0)
            elif direction == "positive":
                noise = rng.uniform(0, noise_range)
            else:
                noise = rng.uniform(-noise_range, noise_range)
            communicated = actual_amount + noise
            communicated = max(0, min(communicated, max_amount))
        elif noise_type == "probabilistic":
            prob = self.noise_config.get("probability", 0)
            if rng.random() < prob:
                replacement = self.noise_config.get("replacement", "random")
                if replacement == "random":
                    communicated = rng.uniform(0, max_amount)
                elif replacement == "zero":
                    communicated = 0
                elif replacement == "max":
                    communicated = max_amount
                else:
                    communicated = actual_amount
            else:
                communicated = actual_amount
        else:
            communicated = actual_amount

        return round(communicated, 2), actual_amount

    def _apply_noise_for_event(
        self,
        actual_amount,
        max_amount,
        *,
        turn,
        dyad_id,
        action_type,
    ):
        if self.noise_seed is None:
            return self._apply_noise(actual_amount, max_amount)
        seed_material = (
            f"{self.noise_seed}|{turn}|{dyad_id}|{action_type}".encode("utf-8")
        )
        event_seed = int.from_bytes(
            hashlib.sha256(seed_material).digest()[:8],
            "big",
        )
        return self._apply_noise(
            actual_amount,
            max_amount,
            rng=random.Random(event_seed),
        )

    def _should_apply_noise_to(self, action_type):
        applies_to = self.noise_config.get("applies_to", "sent")
        return applies_to == "both" or applies_to == action_type

    def _role_display_name(self, pairing, role):
        agent_id = pairing[role]
        if len(self.agent_ids) > 2 or self.prompt_regime == "unified":
            if not self.names_visible_in_prompts():
                return "the sender" if role == "investor" else "the receiver"
            return self.get_agent_display_name(agent_id)
        return self.other_player_names[role]

    def _validate_history_policy(self, history_policy):
        normalized = str(history_policy or "minimal").strip().lower()
        if normalized not in self.VALID_HISTORY_POLICIES:
            choices = ", ".join(sorted(self.VALID_HISTORY_POLICIES))
            raise ValueError(
                f"history_policy must be one of: {choices}; got {history_policy!r}"
            )
        return normalized

    def _validate_prompt_regime(self, prompt_regime):
        normalized = str(prompt_regime or "legacy").strip().lower()
        if normalized not in self.VALID_PROMPT_REGIMES:
            choices = ", ".join(sorted(self.VALID_PROMPT_REGIMES))
            raise ValueError(
                f"prompt_regime must be one of: {choices}; got {prompt_regime!r}"
            )
        return normalized

    def _validate_punishment_prompt_variant(self, variant):
        normalized = str(variant or "current").strip().lower()
        if normalized not in self.VALID_PUNISHMENT_PROMPT_VARIANTS:
            choices = ", ".join(sorted(self.VALID_PUNISHMENT_PROMPT_VARIANTS))
            raise ValueError(
                "punishment_prompt_variant must be one of: "
                f"{choices}; got {variant!r}"
            )
        return normalized

    def _finalize_game_prompt(self, prompt, agent_id, opponent_id):
        if self.history_policy == "relative_pair_ids":
            identity_context = (
                "ROUND-LOCAL PAIR IDS:\n"
                "- Your round-local pair ID is Member Self.\n"
                "- Your current co-player's round-local pair ID is Member Other.\n"
                "- These neutral pair IDs are reassigned every round and do not "
                "reveal agent names.\n"
                "- No population-wide interaction history is shown in this condition."
            )
            prompt = f"{identity_context}\n\n{prompt}"
        elif self.history_policy == "stable_ids":
            identity_context = (
                "STABLE POPULATION IDS:\n"
                f"- Your stable population ID is {self.public_ledger_label(agent_id)}.\n"
                "- Your current co-player's stable population ID is "
                f"{self.public_ledger_label(opponent_id)}.\n"
                "- These neutral IDs stay the same across rounds and do not reveal "
                "agent names.\n"
                "- No population-wide interaction history is shown in this condition."
            )
            prompt = f"{identity_context}\n\n{prompt}"
        elif self.history_policy == "anonymous_population_record":
            record_context = (
                "ANONYMOUS POPULATION RECORD:\n"
                "- Before each game decision, every agent sees the same record of "
                "communicated/noisy transfers from recent completed population rounds.\n"
                "- Historical pairs are relabeled independently in every round, so "
                "the record cannot identify your current co-player or track individuals.\n"
                "- The record does not reveal hidden true amounts."
            )
            prompt = f"{record_context}\n\n{prompt}"
        elif self.history_policy == "population_ledger":
            ledger_context = (
                "PUBLIC POPULATION LEDGER:\n"
                f"- Your stable public ID is {self.public_ledger_label(agent_id)}.\n"
                "- Your current co-player's stable public ID is "
                f"{self.public_ledger_label(opponent_id)}.\n"
                "- Before each game decision, every agent sees the same ledger of "
                "communicated/noisy transfers from recent completed population rounds. "
                "The ledger does not reveal hidden true amounts."
            )
            prompt = f"{ledger_context}\n\n{prompt}"
        if self.game_prompt_addition:
            prompt = (
                f"{prompt.rstrip()}\n\n"
                f"{self.game_prompt_addition}\n"
            )
        return self.with_prompt_context(prompt, agent_id, opponent_id)

    def get_system_prompt(self, agent_id, agent):
        if not self.system_prompt_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments_noisy.yaml under "
                "prompt_templates, named 'trust_game_default' (or your custom template name)"
            )

        base_prompt = self.system_prompt_template.format(
            endowment=self.endowment,
            multiplier=self.multiplier,
        )

        if agent_id in self.personas and self.personas[agent_id].get("system_addition"):
            base_prompt += f"\n\n{self.personas[agent_id]['system_addition']}"

        if self.noise_config.get("inform_agents", False):
            if self.noise_semantics == "environmental":
                base_prompt += (
                    "\n\nNOTE: Transfer amounts may be perturbed by the environment "
                    "after you choose them.\n"
                    "Your earnings are based on the amounts that actually arrive."
                )
            else:
                base_prompt += (
                    "\n\nNOTE: There may be communication noise in this game.\n"
                    "The amounts you see may differ slightly from what was actually "
                    "sent/returned.\n"
                    "This is part of the experimental design."
                )

        if self.punishment_enabled:
            base_prompt += (
                "\n\nDEDUCTION-POINT STAGE:\n"
                "- After the receiver returns, the sender receives a separate "
                f"budget of {self.punishment_budget} deduction points.\n"
                "- The sender may spend any whole number of those points. "
                "Unspent points are added to the sender's earnings.\n"
                "- Each point spent reduces the receiver's payoff for that round "
                f"by up to ${self.punishment_effect_multiplier:g}; the receiver's "
                "round payoff cannot fall below $0.\n"
                "- The receiver is told the deduction decision and its effect."
            )
            if self.punishment_prompt_variant == "cost_salient":
                base_prompt += (
                    "\n- Spending is optional: choosing 0 is valid, and there is "
                    "no requirement to use the deduction budget."
                    "\n- Because unspent points are added to the sender's earnings, "
                    "each point spent costs the sender $1 relative to keeping it."
                )

        return self.with_system_context(base_prompt, agent_id)

    def get_game_prompt_round_1(self, agent_id, agent, turn):
        pairing = self.get_pairing_for_agent(agent_id, turn)
        opponent_id = self.get_opponent_id(agent_id, turn)
        sim_data = getattr(self, "sim_data_ref", None)
        legacy_context = self._legacy_prompt_context(
            agent_id,
            opponent_id,
            sim_data,
            turn,
        )

        if agent_id == pairing["investor"]:
            if not self.round1_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_round1_investor'"
                )
            prompt = self.round1_investor_template.format(
                endowment=self.endowment,
                agent_name=self.self_prompt_label(agent_id),
                opponent_name=self.current_coplayer_label(opponent_id),
                investor_name=self._role_display_name(pairing, "investor"),
                trustee_name=self._role_display_name(pairing, "trustee"),
                **legacy_context,
            )
            return self._finalize_game_prompt(prompt, agent_id, opponent_id)

        sent_actual = self.sim_data_ref.game_data.get("pending_sents", {}).get(pairing["dyad_id"])
        if sent_actual is None:
            raise ValueError("pending_sent not found in game_data. Investor should have responded first.")

        sent_communicated = self._communicated_sent_for_prompt(
            sim_data=self.sim_data_ref,
            pairing=pairing,
            sent_actual=sent_actual,
        )
        received = sent_communicated * self.multiplier
        percentage = sent_communicated / self.endowment * 100

        if not self.round1_trustee_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments_noisy.yaml under "
                "prompt_templates, named 'trust_game_round1_trustee'"
            )
        prompt = self.round1_trustee_template.format(
            sent=sent_communicated,
            percentage=percentage,
            received=received,
            agent_name=self.self_prompt_label(agent_id),
            opponent_name=self.current_coplayer_label(opponent_id),
            investor_name=self._role_display_name(pairing, "investor"),
            trustee_name=self._role_display_name(pairing, "trustee"),
            **legacy_context,
        )
        return self._finalize_game_prompt(prompt, agent_id, opponent_id)

    def get_game_prompt_later_round(self, agent_id, turn, sim_data, last_responses):
        if len(self.agent_ids) > 2 or self.prompt_regime == "unified":
            return self._get_multi_agent_later_prompt(agent_id, turn, sim_data)

        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        opponent_id = self.get_opponent_id(agent_id, turn, sim_data)
        roles = self.get_roles_for_round(turn, sim_data)
        last_round = self.find_last_completed_dyad_for_agent(agent_id, turn, sim_data)
        if last_round is None:
            return self.get_game_prompt_round_1(agent_id, None, turn)
        legacy_context = self._legacy_prompt_context(
            agent_id,
            opponent_id,
            sim_data,
            turn,
        )

        balances = (
            sim_data.game_data.get("balances_communicated")
            or sim_data.game_data["balances"]
        )
        agent_balance = balances[agent_id]

        if agent_id == roles["investor"]:
            lr_sent = last_round.get("sent_communicated", last_round["sent"])
            lr_received = lr_sent * self.multiplier
            lr_returned = last_round["returned"]
            lr_sent_pct = lr_sent / self.endowment * 100
            lr_trustee_payoff = lr_received - lr_returned

            if not self.later_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments_noisy.yaml under "
                    "prompt_templates, named 'trust_game_later_investor'"
                )
            prompt = self.later_investor_template.format(
                turn=turn,
                last_round_sent=lr_sent,
                last_round_sent_percentage=lr_sent_pct,
                last_round_received=lr_received,
                last_round_returned=lr_returned,
                last_round_trustee_payoff=lr_trustee_payoff,
                agent_balance=agent_balance,
                endowment=self.endowment,
                agent_name=self.self_prompt_label(agent_id),
                opponent_name=self.current_coplayer_label(opponent_id),
                investor_name=self._role_display_name(pairing, "investor"),
                trustee_name=self._role_display_name(pairing, "trustee"),
                **legacy_context,
            )
            return self._finalize_game_prompt(prompt, agent_id, opponent_id)

        sent_actual = sim_data.game_data.get("pending_sents", {}).get(
            pairing["dyad_id"]
        )
        if sent_actual is None:
            raise ValueError(
                "pending_sent not found in game_data. Investor should have responded first."
            )
        sent_communicated = self._communicated_sent_for_prompt(
            sim_data, pairing, sent_actual
        )
        received = sent_communicated * self.multiplier

        lr_sent = last_round["sent"]
        lr_received = last_round["sent"] * self.multiplier
        lr_returned = last_round.get("returned_communicated", last_round["returned"])
        lr_sent_pct = lr_sent / self.endowment * 100
        lr_investor_payoff = self.endowment - lr_sent + lr_returned

        if not self.later_trustee_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments_noisy.yaml under "
                "prompt_templates, named 'trust_game_later_trustee'"
            )
        prompt = self.later_trustee_template.format(
            turn=turn,
            last_round_sent=lr_sent,
            last_round_sent_percentage=lr_sent_pct,
            last_round_received=lr_received,
            last_round_returned=lr_returned,
            last_round_investor_payoff=lr_investor_payoff,
            agent_balance=agent_balance,
            current_round_sent=sent_communicated,
            current_round_sent_percentage=sent_communicated / self.endowment * 100,
            received=received,
            agent_name=self.self_prompt_label(agent_id),
            opponent_name=self.current_coplayer_label(opponent_id),
            investor_name=self._role_display_name(pairing, "investor"),
            trustee_name=self._role_display_name(pairing, "trustee"),
            **legacy_context,
        )
        return self._finalize_game_prompt(prompt, agent_id, opponent_id)

    def _get_multi_agent_later_prompt(self, agent_id, turn, sim_data):
        """Build the shared later-round prompt used by every unified cell."""
        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        opponent_id = self.get_opponent_id(agent_id, turn, sim_data)
        role = pairing["roles"][agent_id]
        balances = sim_data.game_data.get("balances_communicated") or sim_data.game_data["balances"]
        agent_balance = balances[agent_id]
        history = self._format_multi_agent_history(agent_id, opponent_id, turn, sim_data)
        history_block = f"{history}\n" if history else ""

        if role == "investor":
            prompt = (
                f"Round {turn}\n\n"
                f"{history_block}"
                f"Your total visible earnings across all rounds are ${agent_balance}.\n\n"
                f"This round, you are the SENDER against {self.current_coplayer_label(opponent_id)}. "
                f"You have ${self.endowment}. How much do you send? (0-{self.endowment})\n"
                f"Respond exactly as JSON: {{'send': <amount>}}"
            )
        else:
            sent_actual = sim_data.game_data["pending_sents"].get(pairing["dyad_id"])
            if sent_actual is None:
                raise ValueError("pending_sent not found in game_data. Investor should have responded first.")
            sent_communicated = self._communicated_sent_for_prompt(sim_data, pairing, sent_actual)
            received = sent_communicated * self.multiplier
            prompt = (
                f"Round {turn}\n\n"
                f"{history_block}"
                f"Your total visible earnings across all rounds are ${agent_balance}.\n\n"
                f"This round, you are the RECEIVER against {self.current_coplayer_label(opponent_id)}. "
                f"They sent you ${sent_communicated}, so you received ${received}. "
                f"How much do you return? (0-{received})\n"
                f"Respond exactly as JSON: {{'return': <amount>}}"
            )

        return self._finalize_game_prompt(prompt, agent_id, opponent_id)

    def _coerce_history_window(self, value, default):
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return default

    def _format_multi_agent_history(self, agent_id, opponent_id, turn, sim_data):
        if self.history_policy == "none":
            return ""
        if self.history_policy == "stable_ids":
            return ""
        if self.history_policy == "relative_pair_ids":
            return ""
        if self.history_policy == "population_ledger":
            return self._format_population_ledger(turn, sim_data)
        if self.history_policy == "anonymous_population_record":
            return self._format_anonymous_population_record(turn, sim_data)
        if self.history_policy != "self_and_coplayer":
            return self._format_most_recent_self_history(
                agent_id,
                turn,
                sim_data,
                current_coplayer_id=opponent_id,
            )

        # A window of 0 drops that section entirely (memory-primary mode keeps
        # self history in chat memory, so only the co-player block is injected).
        if self.self_history_window == 0 and self.coplayer_history_window == 0:
            return ""

        lines = ["Visible history before this round:"]

        if self.self_history_window > 0:
            self_history = self.find_completed_dyads_for_agent(
                agent_id,
                turn,
                sim_data,
                limit=self.self_history_window,
            )
            lines.append(f"Your last {self.self_history_window} game(s):")
            if self_history:
                lines.extend(
                    f"- {self._format_visible_history_entry_for_agent(agent_id, dyad, current_coplayer_id=opponent_id)}"
                    for dyad in self_history
                )
            else:
                lines.append("- No previous completed games involving you.")

        if self.coplayer_history_window > 0:
            coplayer_history = self.find_completed_dyads_for_agent(
                opponent_id,
                turn,
                sim_data,
                limit=self.coplayer_history_window,
            )
            opponent_name = self.current_coplayer_label(opponent_id)
            lines.append(f"{self.coplayer_history_heading(opponent_id)} last {self.coplayer_history_window} game(s):")
            if coplayer_history:
                lines.extend(
                    f"- {self._format_visible_history_entry_for_agent(opponent_id, dyad, observer_agent_id=agent_id)}"
                    for dyad in coplayer_history
                )
            else:
                lines.append(f"- No previous completed games involving {opponent_name}.")

        return "\n".join(lines)

    def _format_population_ledger(self, turn, sim_data):
        completed_rounds = []
        for entry in getattr(sim_data, "conversation_history", []) or []:
            try:
                entry_round = int(entry.get("round", 0))
            except (TypeError, ValueError):
                continue
            if entry_round >= turn:
                continue
            completed_rounds.append((entry_round, entry))

        completed_rounds.sort(key=lambda item: item[0])
        completed_rounds = completed_rounds[-self.population_history_window :]
        if not completed_rounds:
            return "Public ledger: no previous population round has been completed."

        lines = [
            "Public ledger of communicated/noisy transfers "
            f"(last {self.population_history_window} population round(s)):"
        ]
        for entry_round, entry in completed_rounds:
            for dyad in self.iter_completed_dyads(entry):
                investor_id = dyad.get("investor")
                trustee_id = dyad.get("trustee")
                sent = dyad.get("sent_communicated")
                returned = dyad.get("returned_communicated")
                if investor_id is None or trustee_id is None:
                    raise ValueError(
                        f"Public ledger round {entry_round} has incomplete agent IDs."
                    )
                if sent is None or returned is None:
                    raise ValueError(
                        "Public ledger requires communicated transfer values; "
                        f"round {entry_round} is incomplete."
                    )
                lines.append(
                    f"- Round {entry_round}: {self.public_ledger_label(investor_id)} "
                    f"(SENDER) sent ${sent} to {self.public_ledger_label(trustee_id)} "
                    f"(RECEIVER); {self.public_ledger_label(trustee_id)} returned "
                    f"${returned}."
                )
        return "\n".join(lines)

    def _format_anonymous_population_record(self, turn, sim_data):
        completed_rounds = []
        for entry in getattr(sim_data, "conversation_history", []) or []:
            try:
                entry_round = int(entry.get("round", 0))
            except (TypeError, ValueError):
                continue
            if entry_round >= turn:
                continue
            completed_rounds.append((entry_round, entry))

        completed_rounds.sort(key=lambda item: item[0])
        completed_rounds = completed_rounds[-self.population_history_window :]
        if not completed_rounds:
            return "Anonymous population record: no previous round has been completed."

        lines = [
            "Anonymous record of communicated/noisy population transfers "
            f"(last {self.population_history_window} population round(s)):"
        ]
        for entry_round, entry in completed_rounds:
            for pair_index, dyad in enumerate(
                self.iter_completed_dyads(entry),
                start=1,
            ):
                sent = dyad.get("sent_communicated")
                returned = dyad.get("returned_communicated")
                if sent is None or returned is None:
                    raise ValueError(
                        "Anonymous population record requires communicated transfer "
                        f"values; round {entry_round} is incomplete."
                    )
                lines.append(
                    f"- Round {entry_round}, Pair {pair_index}: a sender sent "
                    f"${sent}; the receiver returned ${returned}."
                )
        return "\n".join(lines)

    def _format_most_recent_self_history(
        self,
        agent_id,
        turn,
        sim_data,
        current_coplayer_id=None,
    ):
        last_dyad = self.find_last_completed_dyad_for_agent(agent_id, turn, sim_data)
        if not last_dyad:
            return "No previous game round involving you has been completed."

        last_opponent_id = self.get_opponent_from_dyad(last_dyad, agent_id)
        last_opponent_name = self.history_coplayer_label(
            last_opponent_id,
            current_coplayer_id=current_coplayer_id,
        )
        last_role = last_dyad["roles"].get(agent_id)
        if last_role == "investor":
            lr_returned = last_dyad.get("returned_communicated", last_dyad["returned"])
            lr_payoff = self.endowment - last_dyad["sent"] + lr_returned
            return (
                f"In your most recent previous game round, you were the SENDER "
                f"against {last_opponent_name}. You sent ${last_dyad['sent']}, "
                f"it became ${last_dyad['received']}, and you saw them return "
                f"${lr_returned} to you. Your visible payoff was ${lr_payoff}."
            )
        if last_role == "trustee":
            lr_sent = last_dyad.get("sent_communicated", last_dyad["sent"])
            lr_received = last_dyad.get("received_communicated", lr_sent * self.multiplier)
            lr_payoff = lr_received - last_dyad["returned"]
            return (
                f"In your most recent previous game round, you were the RECEIVER "
                f"against {last_opponent_name}. You saw them send ${lr_sent}, "
                f"it became ${lr_received}, and you returned ${last_dyad['returned']}. "
                f"Your visible payoff was ${lr_payoff}."
            )
        return "No previous game round involving you has been completed."

    def _format_visible_history_entry_for_agent(
        self,
        agent_id,
        dyad,
        observer_agent_id=None,
        current_coplayer_id=None,
    ):
        round_number = dyad.get("round", "?")
        opponent_id = self.get_opponent_from_dyad(dyad, agent_id)
        opponent_name = self.history_coplayer_label(
            opponent_id,
            observer_agent_id=observer_agent_id,
            current_coplayer_id=current_coplayer_id,
        )
        role = dyad["roles"].get(agent_id)
        visible_payoff = dyad.get("payoffs_communicated", {}).get(agent_id)
        if role == "investor":
            returned = dyad.get("returned_communicated", dyad["returned"])
            return (
                f"Round {round_number} against {opponent_name}, as SENDER: "
                f"sent ${dyad['sent']}, it became ${dyad['received']}, "
                f"saw ${returned} returned, visible payoff ${visible_payoff}."
            )
        if role == "trustee":
            sent = dyad.get("sent_communicated", dyad["sent"])
            received = dyad.get("received_communicated", sent * self.multiplier)
            return (
                f"Round {round_number} against {opponent_name}, as RECEIVER: "
                f"saw ${sent} sent, it became ${received}, "
                f"returned ${dyad['returned']}, visible payoff ${visible_payoff}."
            )
        return f"Round {round_number} against {opponent_name}: role and payoff unavailable."

    def _communicated_sent_for_prompt(self, sim_data, pairing, sent_actual):
        dyad_id = pairing["dyad_id"]
        pending = sim_data.game_data.setdefault("pending_sents_communicated", {})
        if dyad_id in pending:
            return pending[dyad_id]
        if self._should_apply_noise_to("sent"):
            sent_communicated, _ = self._apply_noise_for_event(
                sent_actual,
                self.endowment,
                turn=pairing["round"],
                dyad_id=dyad_id,
                action_type="sent",
            )
        else:
            sent_communicated = sent_actual
        pending[dyad_id] = sent_communicated
        sim_data.game_data["pending_sent_communicated"] = sent_communicated
        return sent_communicated

    def process_intermediate_response(self, agent_id, response, turn, sim_data):
        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        if agent_id != pairing["investor"]:
            return

        sent_raw = self._extract_amount(response, "send")
        sent_amount, _ = self._bounded_amount(sent_raw, self.endowment)
        sim_data.game_data.setdefault("pending_sents", {})[pairing["dyad_id"]] = sent_amount
        sim_data.game_data["pending_sent"] = sent_amount
        self.sim_data_ref = sim_data

    def process_turn(self, turn, agent_responses, sim_data):
        self._ensure_balances(sim_data)
        pairings = self.get_round_pairings(turn, sim_data)

        dyads = []
        round_actions = {}
        round_payoffs = {}
        last_responses = {}

        for pairing in pairings:
            investor_id = pairing["investor"]
            trustee_id = pairing["trustee"]
            sent_raw = self._extract_amount(agent_responses[investor_id], "send")
            sent_decision, sent_clamped = self._bounded_amount(
                sent_raw,
                self.endowment,
            )

            sent_after_noise = sim_data.game_data.get(
                "pending_sents_communicated",
                {},
            ).get(
                pairing["dyad_id"],
            )
            if sent_after_noise is None:
                sent_after_noise = self._communicated_sent_for_prompt(
                    sim_data,
                    pairing,
                    sent_decision,
                )
            if self.noise_semantics == "environmental":
                sent_actual = sent_after_noise
                sent_communicated = sent_actual
            else:
                sent_actual = sent_decision
                sent_communicated = sent_after_noise
            received_actual = sent_actual * self.multiplier
            received_communicated = sent_communicated * self.multiplier
            returned_raw = self._extract_amount(agent_responses[trustee_id], "return")
            returned_decision, returned_clamped = self._bounded_amount(
                returned_raw,
                received_actual,
            )

            if self._should_apply_noise_to("returned"):
                returned_after_noise, _ = self._apply_noise_for_event(
                    returned_decision,
                    received_actual,
                    turn=turn,
                    dyad_id=pairing["dyad_id"],
                    action_type="returned",
                )
            else:
                returned_after_noise = returned_decision

            if self.noise_semantics == "environmental":
                returned_actual = returned_after_noise
                returned_communicated = returned_actual
            else:
                returned_actual = returned_decision
                returned_communicated = returned_after_noise

            investor_payoff = (self.endowment - sent_actual) + returned_actual
            trustee_payoff = received_actual - returned_actual
            investor_payoff_communicated = (self.endowment - sent_actual) + returned_communicated
            trustee_payoff_communicated = received_communicated - returned_actual

            sim_data.game_data["balances"][investor_id] += investor_payoff
            sim_data.game_data["balances"][trustee_id] += trustee_payoff
            sim_data.game_data["balances_communicated"][investor_id] += investor_payoff_communicated
            sim_data.game_data["balances_communicated"][trustee_id] += trustee_payoff_communicated

            sent_noise = round(sent_after_noise - sent_decision, 2)
            returned_noise = round(returned_after_noise - returned_decision, 2)
            noise_applied = sent_noise != 0 or returned_noise != 0
            if noise_applied:
                stats = sim_data.game_data["noise_stats"]
                stats["rounds_with_noise"] += 1
                stats["total_sent_noise"] += abs(sent_noise)
                stats["total_returned_noise"] += abs(returned_noise)
            action_validation = {
                "sent": {
                    "raw": sent_raw,
                    "amount": sent_decision,
                    "min": 0,
                    "max": self.endowment,
                    "clamped": sent_clamped,
                },
                "returned": {
                    "raw": returned_raw,
                    "amount": returned_decision,
                    "min": 0,
                    "max": received_actual,
                    "clamped": returned_clamped,
                },
            }
            investor_action = {
                "action": "sent",
                "amount": sent_actual,
                "communicated": sent_communicated,
                "decision": sent_decision,
                "noise": sent_noise,
            }
            trustee_action = {
                "action": "returned",
                "amount": returned_actual,
                "communicated": returned_communicated,
                "decision": returned_decision,
                "noise": returned_noise,
            }
            if sent_clamped:
                investor_action["raw_amount"] = sent_raw
                investor_action["clamped"] = True
            if returned_clamped:
                trustee_action["raw_amount"] = returned_raw
                trustee_action["clamped"] = True

            dyad = {
                **pairing,
                "sent": sent_actual,
                "sent_decision": sent_decision,
                "sent_noise": sent_noise,
                "sent_communicated": sent_communicated,
                "received": received_actual,
                "received_communicated": received_communicated,
                "returned": returned_actual,
                "returned_decision": returned_decision,
                "returned_noise": returned_noise,
                "returned_communicated": returned_communicated,
                "investor_payoff": investor_payoff,
                "trustee_payoff": trustee_payoff,
                "investor_payoff_communicated": investor_payoff_communicated,
                "trustee_payoff_communicated": trustee_payoff_communicated,
                "payoffs": {
                    investor_id: investor_payoff,
                    trustee_id: trustee_payoff,
                },
                "payoffs_communicated": {
                    investor_id: investor_payoff_communicated,
                    trustee_id: trustee_payoff_communicated,
                },
                "balances": dict(sim_data.game_data["balances"]),
                "balances_communicated": dict(sim_data.game_data["balances_communicated"]),
                "noise_semantics": self.noise_semantics,
                "noise_applied": noise_applied,
                "action_validation": action_validation,
                "other_player_names": self.other_player_names,
                "actions": {
                    investor_id: investor_action,
                    trustee_id: trustee_action,
                },
            }
            dyads.append(dyad)
            round_actions.update(dyad["actions"])
            round_payoffs.update(dyad["payoffs"])
            last_responses[investor_id] = {
                "sent": sent_actual,
                "sent_decision": sent_decision,
                "sent_communicated": sent_communicated,
            }
            last_responses[trustee_id] = {
                "returned": returned_actual,
                "returned_decision": returned_decision,
                "returned_communicated": returned_communicated,
            }

        sim_data.game_data["pending_sents"] = {}
        sim_data.game_data["pending_sents_communicated"] = {}
        sim_data.game_data["pending_sent"] = 0
        sim_data.game_data["pending_sent_communicated"] = 0
        self._fill_round_entry(turn, sim_data, dyads, round_actions, round_payoffs)
        return last_responses

    def has_post_game_stage(self):
        """Whether the optional sender deduction stage should be executed."""
        return self.punishment_enabled

    def get_post_game_move_order(self, turn, sim_data):
        if not self.punishment_enabled:
            return []
        return [
            pairing["investor"]
            for pairing in self.get_round_pairings(turn, sim_data)
        ]

    def _current_round_dyad_for_agent(self, agent_id, turn, sim_data):
        entry = next(
            (
                item
                for item in reversed(sim_data.conversation_history)
                if item.get("round") == turn
            ),
            None,
        )
        if entry is None:
            raise ValueError(f"Round {turn} entry not found for deduction stage.")
        dyad = next(
            (
                item
                for item in entry.get("dyads", [])
                if agent_id in item.get("agents", [])
            ),
            None,
        )
        if dyad is None:
            raise ValueError(
                f"Completed round {turn} dyad not found for {agent_id}."
            )
        return entry, dyad

    def get_post_game_prompt(self, agent_id, turn, sim_data):
        if not self.punishment_enabled:
            raise ValueError("Deduction stage is not enabled.")
        _, dyad = self._current_round_dyad_for_agent(
            agent_id,
            turn,
            sim_data,
        )
        if agent_id != dyad["investor"]:
            raise ValueError("Only the sender chooses deduction points.")

        opponent_id = dyad["trustee"]
        visible_return = dyad.get("returned_communicated", dyad["returned"])
        visible_sender_payoff = dyad.get(
            "investor_payoff_communicated",
            dyad["investor_payoff"],
        )
        visible_receiver_payoff = dyad.get(
            "trustee_payoff_communicated",
            dyad["trustee_payoff"],
        )
        prompt = (
            f"Round {turn}: deduction-point stage\n\n"
            f"You saw {self.current_coplayer_label(opponent_id)} return "
            f"${visible_return}. Before the deduction-point budget, your visible "
            f"round payoff is ${visible_sender_payoff} and the receiver's visible "
            f"round payoff is ${visible_receiver_payoff}.\n\n"
            f"You now receive {self.punishment_budget} deduction points. You may "
            f"spend any whole number from 0 to {self.punishment_budget}; unspent "
            "points are added to your earnings. Each point spent reduces the "
            f"receiver's payoff by up to ${self.punishment_effect_multiplier:g}, "
            "without taking it below $0.\n"
            "Respond exactly as JSON: {'deduct': <whole number>}"
        )
        if self.punishment_prompt_variant == "cost_salient":
            prompt = (
                prompt.rstrip()
                + "\nSpending is optional: 0 is valid, and there is no requirement "
                "to use the budget. Each point spent costs you $1 relative to "
                "keeping it."
            )
        return self._finalize_game_prompt(prompt, agent_id, opponent_id)

    def validate_post_game_response(self, content):
        amount = self._extract_amount(content, "deduct")
        if not float(amount).is_integer():
            raise ValueError("Deduction points must be a whole number.")
        if not 0 <= amount <= self.punishment_budget:
            raise ValueError(
                "Deduction points must be between 0 and "
                f"{self.punishment_budget}."
            )

    def get_forced_post_game_response(self, agent_id):
        if not self.is_defector(agent_id):
            return None
        if self.defector_action_policy != "forced_zero":
            return None
        return {
            "content": '{"deduct": 0}',
            "reasoning": None,
            "usage": None,
            "response_source": "forced_zero",
        }

    def process_post_game_stage(self, turn, responses, sim_data):
        """Apply sender-funded deduction points and update saved round state."""
        if not self.punishment_enabled:
            return {}

        entry = next(
            (
                item
                for item in reversed(sim_data.conversation_history)
                if item.get("round") == turn
            ),
            None,
        )
        if entry is None:
            raise ValueError(f"Round {turn} entry not found for deduction stage.")

        deduction_records = {}
        for dyad in entry.get("dyads", []):
            investor_id = dyad["investor"]
            trustee_id = dyad["trustee"]
            if investor_id not in responses:
                raise ValueError(
                    f"Missing deduction response for sender {investor_id}."
                )

            raw = self._extract_amount(responses[investor_id], "deduct")
            if not float(raw).is_integer():
                raise ValueError("Deduction points must be a whole number.")
            spent = int(raw)
            if not 0 <= spent <= self.punishment_budget:
                raise ValueError(
                    "Deduction points must be between 0 and "
                    f"{self.punishment_budget}."
                )

            pre_actual = dict(dyad["payoffs"])
            pre_visible = dict(dyad["payoffs_communicated"])
            sender_bonus = self.punishment_budget - spent
            intended_loss = self.punishment_effect_multiplier * spent
            actual_loss = min(intended_loss, pre_actual[trustee_id])
            visible_loss = min(intended_loss, pre_visible[trustee_id])

            investor_payoff = pre_actual[investor_id] + sender_bonus
            trustee_payoff = pre_actual[trustee_id] - actual_loss
            investor_visible = pre_visible[investor_id] + sender_bonus
            trustee_visible = pre_visible[trustee_id] - visible_loss

            sim_data.game_data["balances"][investor_id] += sender_bonus
            sim_data.game_data["balances"][trustee_id] -= actual_loss
            sim_data.game_data["balances_communicated"][investor_id] += sender_bonus
            sim_data.game_data["balances_communicated"][trustee_id] -= visible_loss

            dyad["pre_deduction_payoffs"] = pre_actual
            dyad["pre_deduction_payoffs_communicated"] = pre_visible
            dyad["deduction_budget"] = self.punishment_budget
            dyad["deduction_spent"] = spent
            dyad["deduction_effect_multiplier"] = self.punishment_effect_multiplier
            dyad["deduction_intended_loss"] = intended_loss
            dyad["deduction_actual_loss"] = actual_loss
            dyad["deduction_visible_loss"] = visible_loss
            dyad["investor_payoff"] = investor_payoff
            dyad["trustee_payoff"] = trustee_payoff
            dyad["investor_payoff_communicated"] = investor_visible
            dyad["trustee_payoff_communicated"] = trustee_visible
            dyad["payoffs"] = {
                investor_id: investor_payoff,
                trustee_id: trustee_payoff,
            }
            dyad["payoffs_communicated"] = {
                investor_id: investor_visible,
                trustee_id: trustee_visible,
            }
            dyad["deduction_action"] = {
                "agent_id": investor_id,
                "target_id": trustee_id,
                "spent": spent,
                "intended_loss": intended_loss,
                "actual_loss": actual_loss,
                "visible_loss": visible_loss,
            }
            deduction_records[dyad["dyad_id"]] = dict(dyad["deduction_action"])

        entry["deductions"] = deduction_records
        entry["payoffs"] = {
            agent_id: payoff
            for dyad in entry.get("dyads", [])
            for agent_id, payoff in dyad["payoffs"].items()
        }
        entry["balances"] = dict(sim_data.game_data["balances"])
        entry["balances_communicated"] = dict(
            sim_data.game_data["balances_communicated"]
        )
        final_balances = dict(sim_data.game_data["balances"])
        final_visible_balances = dict(sim_data.game_data["balances_communicated"])
        for dyad in entry.get("dyads", []):
            dyad["balances"] = dict(final_balances)
            dyad["balances_communicated"] = dict(final_visible_balances)
        return deduction_records

    def get_post_game_notification(self, agent_id, turn, sim_data):
        if not self.punishment_enabled:
            raise ValueError("Deduction stage is not enabled.")
        _, dyad = self._current_round_dyad_for_agent(
            agent_id,
            turn,
            sim_data,
        )
        if agent_id != dyad["trustee"]:
            raise ValueError("Only the receiver gets a deduction notification.")
        sender_id = dyad["investor"]
        spent = dyad["deduction_spent"]
        loss = dyad["deduction_visible_loss"]
        prompt = (
            f"Round {turn} deduction result: "
            f"{self.current_coplayer_label(sender_id)} spent {spent} deduction "
            f"point{'s' if spent != 1 else ''}. This reduced your visible round "
            f"payoff by ${loss}. Your visible round payoff after the deduction "
            f"stage is ${dyad['trustee_payoff_communicated']}."
        )
        response = {
            "content": "Acknowledged.",
            "reasoning": None,
            "usage": None,
            "response_source": "deduction_notification",
        }
        return self.with_prompt_context(prompt, agent_id, sender_id), response

    def _ensure_balances(self, sim_data):
        if "balances" not in sim_data.game_data:
            sim_data.game_data["balances"] = {agent_id: 0 for agent_id in self.agent_ids}
        else:
            for agent_id in self.agent_ids:
                sim_data.game_data["balances"].setdefault(agent_id, 0)

        if "balances_communicated" not in sim_data.game_data:
            sim_data.game_data["balances_communicated"] = {
                agent_id: 0 for agent_id in self.agent_ids
            }
        else:
            for agent_id in self.agent_ids:
                sim_data.game_data["balances_communicated"].setdefault(agent_id, 0)

        sim_data.game_data.setdefault("pending_sents", {})
        sim_data.game_data.setdefault("pending_sents_communicated", {})
        sim_data.game_data.setdefault("pending_sent", 0)
        sim_data.game_data.setdefault("pending_sent_communicated", 0)
        sim_data.game_data.setdefault(
            "noise_stats",
            {
                "rounds_with_noise": 0,
                "total_sent_noise": 0,
                "total_returned_noise": 0,
            },
        )
        self.sim_data_ref = sim_data

    def _fill_round_entry(self, turn, sim_data, dyads, round_actions, round_payoffs):
        for entry in sim_data.conversation_history:
            if entry.get("round") != turn:
                continue

            entry["dyads"] = dyads
            entry["pairings"] = [
                {
                    "round": dyad["round"],
                    "dyad_id": dyad["dyad_id"],
                    "agents": dyad["agents"],
                    "investor": dyad["investor"],
                    "trustee": dyad["trustee"],
                    "roles": dyad["roles"],
                    "agent_names": dyad["agent_names"],
                }
                for dyad in dyads
            ]
            entry["roles"] = self.get_roles_by_agent_for_round(turn, sim_data)
            entry["payoffs"] = round_payoffs
            entry["balances"] = dict(sim_data.game_data["balances"])
            entry["balances_communicated"] = dict(sim_data.game_data["balances_communicated"])
            entry["actions"] = round_actions
            entry["action_validation"] = {
                dyad["dyad_id"]: dyad["action_validation"] for dyad in dyads
            }
            entry["other_player_names"] = self.other_player_names
            entry["noise_semantics"] = self.noise_semantics

            if len(dyads) == 1:
                dyad = dyads[0]
                for key in [
                    "sent",
                    "sent_decision",
                    "sent_noise",
                    "sent_communicated",
                    "received",
                    "received_communicated",
                    "returned",
                    "returned_decision",
                    "returned_noise",
                    "returned_communicated",
                    "investor_payoff",
                    "trustee_payoff",
                    "investor_payoff_communicated",
                    "trustee_payoff_communicated",
                    "noise_applied",
                ]:
                    entry[key] = dyad[key]
            else:
                for key in [
                    "sent",
                    "sent_decision",
                    "sent_noise",
                    "sent_communicated",
                    "received",
                    "received_communicated",
                    "returned",
                    "returned_decision",
                    "returned_noise",
                    "returned_communicated",
                    "investor_payoff",
                    "trustee_payoff",
                    "investor_payoff_communicated",
                    "trustee_payoff_communicated",
                    "noise_applied",
                ]:
                    entry[key] = None
            break

    def _bounded_amount(self, amount, max_amount):
        max_amount = max(0, max_amount)
        bounded = max(0, min(amount, max_amount))
        return bounded, bounded != amount

    def _extract_amount(self, response_data, key):
        if isinstance(response_data, str):
            content = response_data
        else:
            content = response_data.get("content", "")

        number = r"\$?\s*(-?\d+(?:\.\d*)?|-?\.\d+)"
        pattern = rf"'{key}':\s*{number}|" + rf'"{key}":\s*{number}'
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if matches:
            return float(next(group for group in matches[0].groups() if group is not None))

        # Sonnet occasionally answers a sender prompt with {"return": 0}, or
        # vice versa, when the surrounding text clearly describes the requested
        # action. Treat this as recoverable only when there is exactly one
        # opposite action amount and the expected key is absent.
        alternate_key = {"send": "return", "return": "send"}.get(key)
        if alternate_key:
            alternate_pattern = (
                rf"'{alternate_key}':\s*{number}|"
                + rf'"{alternate_key}":\s*{number}'
            )
            alternate_matches = list(re.finditer(alternate_pattern, content, re.IGNORECASE))
            if len(alternate_matches) == 1:
                return float(
                    next(group for group in alternate_matches[0].groups() if group is not None)
                )
        raise ValueError(f"Could not extract {key} from: {content[:200]}")

    def print_turn_summary(self, turn, agent_responses, sim_data):
        entry = sim_data.conversation_history[-1]
        dyads = list(self.iter_completed_dyads(entry))

        print(f"\n{'*' * 80}")
        print(f"ROUND {turn} COMPLETE")
        for dyad in dyads:
            investor_id = dyad["investor"]
            trustee_id = dyad["trustee"]
            print(
                f"  {dyad['dyad_id']}: "
                f"{investor_id} ({self.get_agent_display_name(investor_id)}) = Sender, "
                f"{trustee_id} ({self.get_agent_display_name(trustee_id)}) = Receiver"
            )
            print(
                f"    Sent: ${dyad['sent']} -> Received: ${dyad['received']} "
                f"-> Returned: ${dyad['returned']}"
            )
            if dyad.get("noise_applied"):
                if self.noise_semantics == "environmental":
                    print(
                        f"    [NOISE] Decisions sent=${dyad['sent_decision']:.2f}, "
                        f"returned=${dyad['returned_decision']:.2f}; actual ledger "
                        f"sent=${dyad['sent']:.2f}, returned=${dyad['returned']:.2f}"
                    )
                else:
                    print(
                        f"    [NOISE] Communicated sent="
                        f"${dyad['sent_communicated']:.2f}, returned="
                        f"${dyad['returned_communicated']:.2f}"
                    )
            if "deduction_spent" in dyad:
                print(
                    f"    Deduction: sender spent {dyad['deduction_spent']} "
                    f"point(s), receiver lost ${dyad['deduction_actual_loss']}"
                )
            print(
                f"    Payoffs: {investor_id} ${dyad['investor_payoff']}, "
                f"{trustee_id} ${dyad['trustee_payoff']}"
            )

        balances = entry.get("balances") or {}
        cumulative = ", ".join(
            f"{agent_id} ${balances.get(agent_id, 0)}" for agent_id in self.agent_ids
        )
        print(f"  Cumulative: {cumulative}")
        print(f"{'*' * 80}")

    def print_game_summary(self, sim_data):
        total_rounds = max(
            (entry.get("round", 0) for entry in sim_data.conversation_history),
            default=0,
        )
        game_dyads = [
            dyad
            for entry in sim_data.conversation_history
            for dyad in self.iter_completed_dyads(entry)
        ]
        actual_game_dyads = len(game_dyads)
        total_sent = sum(dyad["sent"] for dyad in game_dyads)
        total_returned = sum(dyad["returned"] for dyad in game_dyads)
        avg_sent = total_sent / actual_game_dyads if actual_game_dyads > 0 else 0
        avg_returned = total_returned / actual_game_dyads if actual_game_dyads > 0 else 0

        print("\n" + "=" * 80)
        print("GAME SUMMARY (NOISY)")
        print("=" * 80)
        print(f"\nTotal rounds: {total_rounds}")
        print(f"Dyadic games played: {actual_game_dyads}")
        print(f"Avg sent: ${avg_sent:.2f}/{self.endowment}")
        print(f"Avg returned: ${avg_returned:.2f}")

        balances = sim_data.game_data.get("balances", {})
        final_earnings = ", ".join(
            f"{agent_id} ${balances.get(agent_id, 0)}" for agent_id in self.agent_ids
        )
        print(f"Final earnings: {final_earnings}")

        noise_stats = sim_data.game_data.get("noise_stats", {})
        if noise_stats.get("rounds_with_noise", 0) > 0:
            print("\n--- Noise Statistics ---")
            print(f"  Dyads with noise: {noise_stats['rounds_with_noise']}/{actual_game_dyads}")
            print(f"  Total sent noise: ${noise_stats['total_sent_noise']:.2f}")
            print(f"  Total returned noise: ${noise_stats['total_returned_noise']:.2f}")

        print("\nRole distribution:")
        for agent_id in self.agent_ids:
            investor_rounds = sum(
                1 for dyad in game_dyads if dyad.get("roles", {}).get(agent_id) == "investor"
            )
            trustee_rounds = sum(
                1 for dyad in game_dyads if dyad.get("roles", {}).get(agent_id) == "trustee"
            )
            print(
                f"  {agent_id}: {investor_rounds} rounds as sender, "
                f"{trustee_rounds} rounds as receiver"
            )
