"""Frozen scientific specification for prospective GPT-5.5 gate reruns."""
import hashlib
import json
from pathlib import Path

from experiments.run_noisy_batch import NoisyExperimentConfig, build_noisy_protocol
from src.experiment_condition import build_condition, condition_from_run, digest
from src.llm_settings import prepare_combinations
from src.utils import DIRECT_MODEL_ALIASES

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / 'config/gpt55_gate_rerun.yaml'
CONFIG_SHA256 = '11e5881e561c82a9f3b7e7aaee4a585eb0ac54d1224ed5a6a74a64535b8458ba'
CONTRACT = ROOT / 'tests/fixtures/gpt55_gate_contract.json'
HISTORICAL = {
    0: {'code_commit': 'f53fa6d9fcde5bd10528054423914b03db8881fc',
        'config_sha256': '86f5fff912effffc406352cc05c66f7c38f36725bc72c055073b50ad32c4d137'},
    1: {'code_commit': '2ece1de681e5c99243df9de181cfce43ee94cd5e',
        'config_sha256': 'd204c480b334a5973ec6145abb9d3a6c077430b80e3d2c0d86a373dc892a53ea'},
}


def scientific_condition(condition):
    # Implementations and output locations change for prospective reruns, while
    # every request, protocol and replicate field must match the frozen contract.
    selected = json.loads(json.dumps({k: condition[k] for k in ('llm', 'protocol', 'replicate')}))
    selected['replicate']['identity'].pop('output_path', None)
    return selected


def planned_condition(combo, name):
    game, myth = build_noisy_protocol(combo, 0)
    params = combo['game_params']
    simulation = {
        'num_turns': params['num_turns'], 'num_agents': params['num_agents'],
        'memory_capacity': params['memory_capacity'], 'agent_biases': '',
        'task_order': combo['task_order'], 'agent_names': params.get('agent_names'),
        'seed_myth': None, 'seed_user_prompt': None,
        'chat_memory_mode': params.get('chat_memory_mode', 'default'), 'seed_reinject': False,
        'initial_system_prompt_template': combo.get('initial_system_prompt_template'),
        'switch_to_game_system_before_game': combo.get('switch_to_game_system_before_game', False),
        'game_response_retry_policy': params['game_response_retry_policy'],
    }
    return build_condition(game, myth, {'llm_request': combo['request_plan'].as_dict()}, simulation,
                           {'experiment': name, 'replicate_id': combo['replicate_id']})


def load_gate():
    if hashlib.sha256(CONFIG.read_bytes()).hexdigest() != CONFIG_SHA256:
        raise ValueError('GPT-5.5 rerun config differs from the frozen specification')
    config = NoisyExperimentConfig(str(CONFIG))
    expected = frozen_contract()
    jobs = {}
    for name, definition in config.config['experiment_sets'].items():
        combos = prepare_combinations(config.get_experiment_combinations(name), definition, DIRECT_MODEL_ALIASES)
        if len(combos) != 1:
            raise ValueError(f'{name}: expected exactly one replicate')
        combo = combos[0]
        observed = {'inputs': digest(combo['comparison_inputs']),
                    'condition': digest(scientific_condition(planned_condition(combo, name)))}
        if observed != expected.get(name):
            raise ValueError(f'{name}: resolved condition differs from the frozen specification')
        jobs[name] = combo
    if set(jobs) != set(expected) or len(jobs) != 12:
        raise ValueError('Expected exactly twelve frozen gate cells')
    return jobs


def verify_rerun(run, experiment):
    metadata = run['run_metadata']
    condition = condition_from_run(run)
    expected = frozen_contract().get(experiment)
    observed = {'inputs': digest(metadata.get('comparison_inputs')),
                'condition': digest(scientific_condition(condition))}
    if observed != expected or metadata.get('config_sha256') != CONFIG_SHA256:
        raise ValueError(f'{experiment}: saved run differs from the frozen specification')
    if metadata.get('historical_reference') != HISTORICAL[metadata['replicate_id']]:
        raise ValueError(f'{experiment}: missing original code/config reference')
    return condition


def frozen_contract():
    if hashlib.sha256(CONTRACT.read_bytes()).hexdigest() != 'd0dd07ffd6082dee248c258447d6c77635e80dd057a02234bebda76a3cdea384':
        raise ValueError('GPT-5.5 condition contract changed; explicit scientific review required')
    return json.loads(CONTRACT.read_text())
