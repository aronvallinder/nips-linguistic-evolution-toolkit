import random
import re

from games.base_game import Game
from games.dyadic_pairing import DyadicPairingMixin


class TrustGame(DyadicPairingMixin, Game):
    """Trust/Investment game with sequential dyadic moves."""

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
        multiplier_distribution=None,
        history_policy="minimal",
        self_history_window=1,
        coplayer_history_window=0,
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
    ):
        """
        Args:
            endowment: Starting amount for investor each round.
            multiplier: Base multiplier value.
            multiplier_distribution: Dict specifying how multiplier changes over rounds:
                - None or {"type": "fixed"}: Use fixed multiplier value.
                - {"type": "increasing", "start": 1, "step": 1}: Increase by step each round.
                - {"type": "decreasing", "start": 10, "step": 1}: Decrease by step each round.
                - {"type": "random", "min": 1, "max": 5}: Random value each round.
        """
        super().__init__()
        self.endowment = endowment
        self.base_multiplier = multiplier
        self.multiplier_distribution = multiplier_distribution or {"type": "fixed"}
        self.system_prompt_template = system_prompt_template
        self.round1_investor_template = round1_investor_template
        self.round1_trustee_template = round1_trustee_template
        self.later_investor_template = later_investor_template
        self.later_trustee_template = later_trustee_template
        self.personas = personas or {}
        self.history_policy = history_policy or "minimal"
        self.self_history_window = self._coerce_history_window(self_history_window, 1)
        self.coplayer_history_window = self._coerce_history_window(coplayer_history_window, 0)
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
        self._round_multipliers = {}
        self._init_dyadic_agents()

    @property
    def multiplier(self):
        """Backward compatibility: return base multiplier for system prompt."""
        return self.base_multiplier

    def get_multiplier(self, turn):
        """Get the multiplier for a given turn based on distribution type."""
        dist = self.multiplier_distribution
        dist_type = dist.get("type", "fixed")

        if dist_type == "fixed":
            return self.base_multiplier
        if dist_type == "increasing":
            start = dist.get("start", self.base_multiplier)
            step = dist.get("step", 1)
            return start + (turn - 1) * step
        if dist_type == "decreasing":
            start = dist.get("start", self.base_multiplier)
            step = dist.get("step", 1)
            return max(0, start - (turn - 1) * step)
        if dist_type == "random":
            if turn not in self._round_multipliers:
                min_val = dist.get("min", 1)
                max_val = dist.get("max", 5)
                self._round_multipliers[turn] = random.uniform(min_val, max_val)
            return self._round_multipliers[turn]

        return self.base_multiplier

    def get_system_prompt(self, agent_id, agent):
        """Role-agnostic system prompt that covers both roles."""
        if not self.system_prompt_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'trust_game_default' (or your custom template name)"
            )

        base_prompt = self.system_prompt_template.format(
            endowment=self.endowment,
            multiplier=self.multiplier,
        )

        if agent_id in self.personas and self.personas[agent_id].get("system_addition"):
            base_prompt += f"\n\n{self.personas[agent_id]['system_addition']}"

        return self.with_system_context(base_prompt, agent_id)

    def get_game_prompt_round_1(self, agent_id, agent, turn):
        """First-turn prompt for the agent's current dyad."""
        pairing = self.get_pairing_for_agent(agent_id, turn)
        opponent_id = self.get_opponent_id(agent_id, turn)

        if agent_id == pairing["investor"]:
            if not self.round1_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_round1_investor'"
                )
            prompt = self.round1_investor_template.format(
                endowment=self.endowment,
                agent_name=self.self_prompt_label(agent_id),
                opponent_name=self.current_coplayer_label(opponent_id),
                investor_name=self.role_prompt_label(pairing["investor"], "investor"),
                trustee_name=self.role_prompt_label(pairing["trustee"], "trustee"),
            )
            return self.with_prompt_context(prompt, agent_id, opponent_id)

        sent = self.sim_data_ref.game_data.get("pending_sents", {}).get(pairing["dyad_id"])
        if sent is None:
            raise ValueError(
                "pending_sent not found in game_data. Investor should have responded first."
            )
        current_multiplier = self.get_multiplier(turn)
        received = sent * current_multiplier
        percentage = sent / self.endowment * 100

        if not self.round1_trustee_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'trust_game_round1_trustee'"
            )
        prompt = self.round1_trustee_template.format(
            sent=sent,
            percentage=percentage,
            received=received,
            agent_name=self.self_prompt_label(agent_id),
            opponent_name=self.current_coplayer_label(opponent_id),
            investor_name=self.role_prompt_label(pairing["investor"], "investor"),
            trustee_name=self.role_prompt_label(pairing["trustee"], "trustee"),
        )
        return self.with_prompt_context(prompt, agent_id, opponent_id)

    def get_game_prompt_later_round(self, agent_id, turn, sim_data, last_responses):
        """Subsequent-turn prompt for the agent's current dyad."""
        if len(self.agent_ids) > 2:
            return self._get_multi_agent_later_prompt(agent_id, turn, sim_data)

        roles = self.get_roles_for_round(turn, sim_data)
        last_round = self.find_last_completed_dyad_for_agent(agent_id, turn, sim_data)
        if last_round is None:
            return self.get_game_prompt_round_1(agent_id, None, turn)

        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        opponent_id = self.get_opponent_id(agent_id, turn, sim_data)
        current_multiplier = self.get_multiplier(turn)
        sent = sim_data.game_data.get("pending_sents", {}).get(pairing["dyad_id"])
        if sent is None:
            sent = sim_data.game_data.get("pending_sent", 0)
        received = sent * current_multiplier
        last_round_sent = last_round["sent"]
        last_round_received = last_round.get("received", last_round_sent * self.base_multiplier)
        last_round_returned = last_round["returned"]
        agent_balance = sim_data.game_data["balances"][agent_id]
        last_round_sent_percentage = last_round_sent / self.endowment * 100
        last_round_trustee_payoff = last_round["trustee_payoff"]
        last_round_investor_payoff = last_round["investor_payoff"]

        if agent_id == roles["investor"]:
            if not self.later_investor_template:
                raise ValueError(
                    "No prompt provided. Provide prompt in config/experiments.yaml under "
                    "prompt_templates, named 'trust_game_later_investor'"
                )
            prompt = self.later_investor_template.format(
                turn=turn,
                last_round_sent=last_round_sent,
                last_round_sent_percentage=last_round_sent_percentage,
                last_round_received=last_round_received,
                last_round_returned=last_round_returned,
                last_round_trustee_payoff=last_round_trustee_payoff,
                agent_balance=agent_balance,
                endowment=self.endowment,
                agent_name=self.self_prompt_label(agent_id),
                opponent_name=self.current_coplayer_label(opponent_id),
                investor_name=self.role_prompt_label(pairing["investor"], "investor"),
                trustee_name=self.role_prompt_label(pairing["trustee"], "trustee"),
            )
            return self.with_prompt_context(prompt, agent_id, opponent_id)

        if not self.later_trustee_template:
            raise ValueError(
                "No prompt provided. Provide prompt in config/experiments.yaml under "
                "prompt_templates, named 'trust_game_later_trustee'"
            )
        prompt = self.later_trustee_template.format(
            turn=turn,
            last_round_sent=last_round_sent,
            last_round_sent_percentage=last_round_sent_percentage,
            last_round_received=last_round_received,
            last_round_returned=last_round_returned,
            last_round_investor_payoff=last_round_investor_payoff,
            agent_balance=agent_balance,
            current_round_sent=sent,
            current_round_sent_percentage=sent / self.endowment * 100,
            received=received,
            agent_name=self.self_prompt_label(agent_id),
            opponent_name=self.current_coplayer_label(opponent_id),
            investor_name=self.role_prompt_label(pairing["investor"], "investor"),
            trustee_name=self.role_prompt_label(pairing["trustee"], "trustee"),
        )
        return self.with_prompt_context(prompt, agent_id, opponent_id)

    def _get_multi_agent_later_prompt(self, agent_id, turn, sim_data):
        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        opponent_id = self.get_opponent_id(agent_id, turn, sim_data)
        role = pairing["roles"][agent_id]
        current_multiplier = self.get_multiplier(turn)
        agent_balance = sim_data.game_data["balances"][agent_id]
        history = self._format_multi_agent_history(agent_id, opponent_id, turn, sim_data)

        if role == "investor":
            prompt = (
                f"Round {turn}\n\n"
                f"{history}\n"
                f"Your total earnings across all rounds are ${agent_balance}.\n\n"
                f"This round, you are the SENDER against {self.current_coplayer_label(opponent_id)}. "
                f"You have ${self.endowment}. How much do you send? (0-{self.endowment})\n"
                f"Respond exactly as JSON: {{'send': <amount>}}"
            )
        else:
            sent = sim_data.game_data.get("pending_sents", {}).get(pairing["dyad_id"])
            if sent is None:
                raise ValueError(
                    "pending_sent not found in game_data. Investor should have responded first."
                )
            received = sent * current_multiplier
            prompt = (
                f"Round {turn}\n\n"
                f"{history}\n"
                f"Your total earnings across all rounds are ${agent_balance}.\n\n"
                f"This round, you are the RECEIVER against {self.current_coplayer_label(opponent_id)}. "
                f"They sent you ${sent}, so you received ${received}. "
                f"How much do you return? (0-{received})\n"
                f"Respond exactly as JSON: {{'return': <amount>}}"
            )

        return self.with_prompt_context(prompt, agent_id, opponent_id)

    def _coerce_history_window(self, value, default):
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return default

    def _format_multi_agent_history(self, agent_id, opponent_id, turn, sim_data):
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

        lines = ["History before this round:"]

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
                    f"- {self._format_history_entry_for_agent(agent_id, dyad, current_coplayer_id=opponent_id)}"
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
                    f"- {self._format_history_entry_for_agent(opponent_id, dyad, observer_agent_id=agent_id)}"
                    for dyad in coplayer_history
                )
            else:
                lines.append(f"- No previous completed games involving {opponent_name}.")

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
        last_payoff = last_dyad.get("payoffs", {}).get(agent_id)
        if last_role == "investor":
            return (
                f"In your most recent previous game round, you were the SENDER "
                f"against {last_opponent_name}. You sent ${last_dyad['sent']}, "
                f"it became ${last_dyad['received']} for them, and they returned "
                f"${last_dyad['returned']} to you. Your payoff was ${last_payoff}."
            )
        if last_role == "trustee":
            return (
                f"In your most recent previous game round, you were the RECEIVER "
                f"against {last_opponent_name}. They sent ${last_dyad['sent']} to you, "
                f"it became ${last_dyad['received']}, and you returned "
                f"${last_dyad['returned']}. Your payoff was ${last_payoff}."
            )
        return "No previous game round involving you has been completed."

    def _format_history_entry_for_agent(
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
        payoff = dyad.get("payoffs", {}).get(agent_id)
        if role == "investor":
            return (
                f"Round {round_number} against {opponent_name}, as SENDER: "
                f"sent ${dyad['sent']}, it became ${dyad['received']}, "
                f"received ${dyad['returned']} back, payoff ${payoff}."
            )
        if role == "trustee":
            return (
                f"Round {round_number} against {opponent_name}, as RECEIVER: "
                f"they sent ${dyad['sent']}, it became ${dyad['received']}, "
                f"returned ${dyad['returned']}, payoff ${payoff}."
            )
        return f"Round {round_number} against {opponent_name}: role and payoff unavailable."

    def process_intermediate_response(self, agent_id, response, turn, sim_data):
        """Called after each investor responds, before that dyad's trustee."""
        pairing = self.get_pairing_for_agent(agent_id, turn, sim_data)
        if agent_id != pairing["investor"]:
            return

        sent_raw = self._extract_amount(response, "send")
        sent_amount, _ = self._bounded_amount(sent_raw, self.endowment)
        sim_data.game_data.setdefault("pending_sents", {})[pairing["dyad_id"]] = sent_amount
        sim_data.game_data["pending_sent"] = sent_amount
        self.sim_data_ref = sim_data

    def process_turn(self, turn, agent_responses, sim_data):
        """Process all dyads for this round."""
        self._ensure_balances(sim_data)
        pairings = self.get_round_pairings(turn, sim_data)
        current_multiplier = self.get_multiplier(turn)

        dyads = []
        round_actions = {}
        round_payoffs = {}
        last_responses = {}

        for pairing in pairings:
            investor_id = pairing["investor"]
            trustee_id = pairing["trustee"]
            sent_raw = self._extract_amount(agent_responses[investor_id], "send")
            sent, sent_clamped = self._bounded_amount(sent_raw, self.endowment)
            received = sent * current_multiplier
            returned_raw = self._extract_amount(agent_responses[trustee_id], "return")
            returned, returned_clamped = self._bounded_amount(returned_raw, received)

            investor_payoff = (self.endowment - sent) + returned
            trustee_payoff = received - returned

            sim_data.game_data["balances"][investor_id] += investor_payoff
            sim_data.game_data["balances"][trustee_id] += trustee_payoff
            action_validation = {
                "sent": {
                    "raw": sent_raw,
                    "amount": sent,
                    "min": 0,
                    "max": self.endowment,
                    "clamped": sent_clamped,
                },
                "returned": {
                    "raw": returned_raw,
                    "amount": returned,
                    "min": 0,
                    "max": received,
                    "clamped": returned_clamped,
                },
            }
            investor_action = {"action": "sent", "amount": sent}
            trustee_action = {"action": "returned", "amount": returned}
            if sent_clamped:
                investor_action["raw_amount"] = sent_raw
                investor_action["clamped"] = True
            if returned_clamped:
                trustee_action["raw_amount"] = returned_raw
                trustee_action["clamped"] = True

            dyad = {
                **pairing,
                "sent": sent,
                "received": received,
                "returned": returned,
                "multiplier": current_multiplier,
                "investor_payoff": investor_payoff,
                "trustee_payoff": trustee_payoff,
                "payoffs": {
                    investor_id: investor_payoff,
                    trustee_id: trustee_payoff,
                },
                "balances": dict(sim_data.game_data["balances"]),
                "action_validation": action_validation,
                "actions": {
                    investor_id: investor_action,
                    trustee_id: trustee_action,
                },
            }
            dyads.append(dyad)
            round_actions.update(dyad["actions"])
            round_payoffs.update(dyad["payoffs"])
            last_responses[investor_id] = {"sent": sent}
            last_responses[trustee_id] = {"returned": returned}

        sim_data.game_data["pending_sents"] = {}
        sim_data.game_data["pending_sent"] = 0
        self._fill_round_entry(turn, sim_data, dyads, round_actions, round_payoffs)
        return last_responses

    def _ensure_balances(self, sim_data):
        if "balances" not in sim_data.game_data:
            sim_data.game_data["balances"] = {agent_id: 0 for agent_id in self.agent_ids}
        else:
            for agent_id in self.agent_ids:
                sim_data.game_data["balances"].setdefault(agent_id, 0)
        sim_data.game_data.setdefault("pending_sents", {})
        sim_data.game_data.setdefault("pending_sent", 0)
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
            entry["actions"] = round_actions
            entry["action_validation"] = {
                dyad["dyad_id"]: dyad["action_validation"] for dyad in dyads
            }

            if len(dyads) == 1:
                dyad = dyads[0]
                entry["sent"] = dyad["sent"]
                entry["received"] = dyad["received"]
                entry["returned"] = dyad["returned"]
                entry["multiplier"] = dyad["multiplier"]
                entry["investor_payoff"] = dyad["investor_payoff"]
                entry["trustee_payoff"] = dyad["trustee_payoff"]
            else:
                entry["sent"] = None
                entry["received"] = None
                entry["returned"] = None
                entry["multiplier"] = self.get_multiplier(turn)
                entry["investor_payoff"] = None
                entry["trustee_payoff"] = None
            break

    def _bounded_amount(self, amount, max_amount):
        max_amount = max(0, max_amount)
        bounded = max(0, min(amount, max_amount))
        return bounded, bounded != amount

    def _extract_amount(self, response_data, key):
        """Extract number from JSON response in structured response data."""
        if isinstance(response_data, str):
            content = response_data
        else:
            content = response_data.get("content", "")

        number = r"\$?\s*(-?\d+(?:\.\d*)?|-?\.\d+)"
        pattern = rf"'{key}':\s*{number}|" + rf'"{key}":\s*{number}'
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return float(next(group for group in match.groups() if group is not None))
        raise ValueError(f"Could not extract {key} from: {content[:200]}")

    def print_turn_summary(self, turn, agent_responses, sim_data):
        """Print round summary."""
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
        """Final game summary."""
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
        print("GAME SUMMARY")
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
