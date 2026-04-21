import yaml
from itertools import product
from typing import Dict, List

class ExperimentConfig:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_experiment_combinations(self, experiment_name: str) -> List[Dict]:
        """Generate all parameter combinations for an experiment set"""
        exp_set = self.config['experiment_sets'][experiment_name]

        # Resolve "all" references
        models = self._resolve_all(exp_set['models'], 'base_models')
        templates = self._resolve_all(exp_set['templates'], 'prompt_templates')
        personas = self._resolve_all(exp_set['personas'], 'personas')
        task_orders = self._resolve_all(exp_set['task_orders'], 'task_orders',
                                       from_game_params=True)
        # Only expand myth_topics if explicitly set, otherwise use "anything" as default
        myth_topics_spec = exp_set.get("myth_topics", None)
        if myth_topics_spec is None:
            # No myth_topics specified - use "anything" as default topic
            myth_topic_ids = ["anything"]
        else:
            myth_topic_ids = self._resolve_all(myth_topics_spec, "myth_topics")

        # Generate all combinations
        combinations = []
        for model, template, persona, order, myth_topic_id in product(
            models, templates, personas, task_orders, myth_topic_ids
        ):
            # Keep non-myth task orders from multiplying across all topics
            if "myth" not in order and myth_topic_id != myth_topic_ids[0]:
                continue

            myth_topic = "" if myth_topic_id == "" else self.config["myth_topics"][myth_topic_id]

            # Determine which myth prompts to use (allows custom prefixes like "instruct_non_coop_")
            myth_prompt_prefix = exp_set.get("myth_prompt_prefix", "")
            myth_default_key = f"{myth_prompt_prefix}myth_writing_default"
            myth_later_key = f"{myth_prompt_prefix}myth_writing_later_rounds"

            combo = {
                "model": self.config["base_models"][model],
                "template": self.config["prompt_templates"][template],
                "persona": self.config["personas"][persona],
                "task_order": order,
                "game_params": self._get_game_params(exp_set.get("game_params", {})),
                "myth_topic_id": myth_topic_id,
                "myth_topic": myth_topic,
                # Add all prompt templates for games and myths
                "trust_game_round1_investor": self.config["prompt_templates"].get("trust_game_round1_investor"),
                "trust_game_round1_trustee": self.config["prompt_templates"].get("trust_game_round1_trustee"),
                "trust_game_later_investor": self.config["prompt_templates"].get("trust_game_later_investor"),
                "trust_game_later_trustee": self.config["prompt_templates"].get("trust_game_later_trustee"),
                "myth_writing_default": self.config["prompt_templates"].get(myth_default_key),
                "myth_writing_later_rounds": self.config["prompt_templates"].get(myth_later_key),
            }
            combinations.append(combo)

        return combinations

    def _resolve_all(self, param, config_key, from_game_params=False):
        if param == "all":
            if from_game_params:
                return self.config['game_parameters'][config_key]
            return list(self.config[config_key].keys())
        return param

    def _get_game_params(self, exp_game_params: Dict) -> Dict:
        """Merge experiment-specific game params with defaults"""
        default_params = self.config['game_parameters'].copy()
        default_params.update(exp_game_params)
        return default_params