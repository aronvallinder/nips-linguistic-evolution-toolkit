# Modular LLM Experimental Framework

A flexible, configuration-driven framework for running behavioral experiments with multiple LLM models, designed for studying agent interactions, trust dynamics, and creative collaboration through games and myth-writing tasks.

## Architecture Overview

This framework uses a modular, configuration-based architecture that separates experimental parameters from code logic, enabling easy replication and systematic experimentation.

### Core Components

```
├── config/
│   └── experiments.yaml      # Central configuration file
├── src/
│   ├── experiment_config.py  # Configuration parser and manager
│   ├── simulation.py         # Main simulation engine
│   ├── agents.py            # LLM agent implementations
│   ├── myth_writer.py       # Creative writing task handler
│   └── utils.py             # Utility functions
├── games/
│   ├── base_game.py         # Abstract game interface
│   └── trust_game.py        # Trust game implementation
├── experiments/
│   ├── run_trust_game.py    # Single experiment runner
│   └── run_trust_game_batch.py  # Batch experiment runner
└── analyses_clean/          # Analysis and visualization tools
```

## Key Features

### 1. Configuration-Driven Design
- **Centralized Configuration**: All experimental parameters defined in `config/experiments.yaml`
- **Modular Components**: Models, prompts, personas, and game parameters are independently configurable
- **Experiment Sets**: Pre-defined experimental conditions with automatic parameter expansion

### 2. Multi-Model Support
- **LLM Integration**: Supports multiple models (Llama, GPT-4, Claude)
- **Model Abstraction**: Easy to add new models through configuration
- **Temperature Control**: Configurable randomness for consistent or varied responses

### 3. Behavioral Personas
- **Personality Injection**: Agents can adopt different behavioral patterns (altruistic, selfish, cautious, risk-taking)
- **System Prompt Modification**: Personas modify agent behavior through targeted prompt additions
- **Consistent Characterization**: Maintains personality across multiple interactions

### 4. Flexible Task Ordering
- **Sequential Tasks**: Support for game-then-myth, myth-then-game, or single-task experiments
- **Cross-Task Influence**: Study how performance in one task affects behavior in another
- **Configurable Combinations**: Easy specification of different task sequences

## Configuration Structure

### Base Models
```yaml
base_models:
  llama70b: "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
  gpt4: "gpt-4-turbo"
  claude: "claude-3-sonnet"
```

### Prompt Templates
```yaml
prompt_templates:
  trust_game_default: |
    You are an agent in a trust game...
    # Detailed game rules and response format
```

### Personas
```yaml
personas:
  altruistic:
    description: "altruistic"
    system_addition: "You tend to prioritize others' welfare..."
```

### Experiment Sets
```yaml
experiment_sets:
  pilot:
    models: ["llama8b"]
    personas: ["neutral", "altruistic"]
    task_orders: [["game", "myth"]]
    game_params:
      num_turns: 5
```

## Usage Guide

### Running Single Experiments

```python
# experiments/run_trust_game.py
from src.simulation import run_simulation
from games.trust_game import TrustGame

# Configure and run single experiment
game = TrustGame(endowment=5, multiplier=3)
sim_data = run_simulation(game, model, ...)
```

### Running Batch Experiments

```bash
# Run specific experiment set
python experiments/run_trust_game_batch.py pilot

# Run all default experiments
python experiments/run_trust_game_batch.py
```

### Creating New Experiment Sets

1. **Add to config/experiments.yaml**:
```yaml
experiment_sets:
  my_experiment:
    models: ["llama70b", "gpt4"]
    personas: "all"  # Expands to all defined personas
    task_orders: [["game"], ["myth"]]
    game_params:
      num_turns: 15
      temperature: 0.9
```

2. **Run the experiment**:
```bash
python experiments/run_trust_game_batch.py my_experiment
```

## Experimental Capabilities

### Trust Game Mechanics
- **Economic Decision-Making**: Agents make investment and return decisions
- **Multi-Round Interaction**: Repeated interactions build or erode trust
- **Role Switching**: Agents alternate between investor and trustee roles
- **Memory Integration**: Agents remember previous interactions (configurable capacity)

### Myth Writing Tasks
- **Creative Collaboration**: Agents write and adapt myths based on others' work
- **Cultural Evolution**: Track how stories evolve through agent interactions
- **Cross-Task Influence**: Study how game performance affects creative expression

### Analysis Features
- **Trajectory Plotting**: Visualize cooperation patterns over time
- **Similarity Analysis**: Measure myth convergence using embeddings
- **N-gram Analysis**: Study linguistic patterns in generated text
- **LIWC Integration**: Psychological text analysis capabilities

## Data Management

### Output Structure
```
data/json/
├── experiment_name/
│   ├── 001_model_persona_taskorder.json
│   ├── 002_model_persona_taskorder.json
│   └── ...
```

### Simulation State
Each experiment saves complete simulation state including:
- Agent decisions and reasoning
- Game outcomes and payoffs
- Generated myths and creative content
- Memory states and conversation history
- Experimental parameters and metadata

## Extending the Framework

### Adding New Games
1. Inherit from `BaseGame` in `games/base_game.py`
2. Implement required methods (`play_turn`, `get_results`, etc.)
3. Add game-specific prompts to configuration

### Adding New Models
1. Update `base_models` in `config/experiments.yaml`
2. Ensure model compatibility in `src/agents.py`

### Adding New Analyses
1. Create analysis scripts in `analyses_clean/`
2. Use saved simulation states from `data/json/`
3. Follow existing patterns for visualization and reporting

## Best Practices

1. **Start Small**: Use `pilot` experiments before running full factorial designs
2. **Version Control**: Track configuration changes alongside code
3. **Reproducibility**: Set consistent random seeds and temperatures
4. **Documentation**: Document new personas and prompt templates clearly
5. **Resource Management**: Monitor API usage for large batch experiments

## Dependencies

- Python 3.8+
- PyYAML for configuration management
- LLM API libraries (OpenAI, Anthropic, etc.)
- Analysis dependencies: numpy, pandas, matplotlib, seaborn
- Text analysis: NLTK, spaCy, sentence-transformers

This modular architecture enables systematic study of LLM behavior across different conditions while maintaining experimental rigor and reproducibility.