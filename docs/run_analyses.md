# Running Analysis Scripts

This document explains how to run the analysis scripts on your simulation data.

## Prerequisites

### Python Dependencies
Make sure you have these packages installed:
```bash
pip install matplotlib numpy scipy scikit-learn sentence-transformers spacy nltk together pydantic
```

### Language Models
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Download NLTK data (if needed)
python -c "import nltk; nltk.download('punkt')"
```

## Quick Start: Automated Analysis

### 1. Run All Analyses for a Task Order
Use the shell script to run all analyses for a specific task order:

```bash
# Run analyses for game-only data
./scripts/run_analyses_clean.sh "game"

# Run analyses for myth-only data
./scripts/run_analyses_clean.sh "myth"

# Run analyses for game-then-myth data
./scripts/run_analyses_clean.sh "game,myth"

# Run analyses for myth-then-game data
./scripts/run_analyses_clean.sh "myth,game"
```

**Input**: `data/json/main_loop/task_order/{TASK_ORDER}.json`
**Output**: `data/plots/task_order/{TASK_ORDER}/`

### 2. Batch Processing (All Task Orders)
Use the Jupyter notebook to run analyses for all task orders:

1. Open `analyses_clean/run_all_analyses.ipynb`
2. Run all cells
3. Results will be generated for all task orders automatically

## Manual Execution: Individual Scripts

### Running Single Analysis Scripts

Each script can be run individually with default paths:

```bash
# Trajectory plotting
python analyses_clean/trajectory_plotting.py

# Word chain evolution
python analyses_clean/word_chain_evolution.py

# Cooperativity analysis
python analyses_clean/cooperativity_analysis.py

# Myth similarity (LLM-based)
python analyses_clean/myth_similarity.py

# Myth similarity (embedding-based)
python analyses_clean/myth_similarity_embedding.py

# Plot myth similarity results
python analyses_clean/plot_myth_similarity.py

# N-gram sentence structure
python analyses_clean/n_gram_sentence_structure.py
```

**Default Input**: `data/json/main_loop/Only_myths_Trust_simulation_state.json`
**Default Output**: Current directory

### Running with Custom Paths

Set environment variables to use custom input/output paths:

```bash
# Example: Custom input and output
ANALYSIS_INPUT_FILE="/path/to/your/data.json" \
ANALYSIS_OUTPUT_DIR="/path/to/output/folder" \
ANALYSIS_TASK_NAME="my_experiment" \
python analyses_clean/trajectory_plotting.py
```

## Analysis Script Details

### 1. Trajectory Plotting (`trajectory_plotting.py`)
- **Purpose**: Visualize cooperation trajectories over rounds
- **Requirements**: Game data (sent/received amounts)
- **Outputs**: Line plots showing cooperation trends

### 2. Word Chain Evolution (`word_chain_evolution.py`)
- **Purpose**: Track how language evolves in myths over time
- **Requirements**: Myth data
- **Outputs**: Word frequency plots, vocabulary growth charts

### 3. Cooperativity Analysis (`cooperativity_analysis.py`)
- **Purpose**: Detailed analysis of cooperative behavior patterns
- **Requirements**: Game data (sent/received amounts)
- **Outputs**: Statistical analysis, cooperation metrics

### 4. Myth Similarity - LLM (`myth_similarity.py`)
- **Purpose**: Compare myth similarities using LLM judgment
- **Requirements**: Myth data, Together AI API key
- **Outputs**: JSON results with multi-dimensional similarity scores
- **Note**: Requires `TOGETHER_API_KEY` environment variable

### 5. Myth Similarity - Embeddings (`myth_similarity_embedding.py`)
- **Purpose**: Compare myth similarities using semantic embeddings
- **Requirements**: Myth data, sentence-transformers library
- **Outputs**: Plots showing semantic similarity over time

### 6. Plot Myth Similarity (`plot_myth_similarity.py`)
- **Purpose**: Visualize results from LLM-based myth similarity analysis
- **Requirements**: Results from `myth_similarity.py`
- **Outputs**: Multiple plots (line charts, heatmaps, box plots)

### 7. N-gram Sentence Structure (`n_gram_sentence_structure.py`)
- **Purpose**: Analyze syntactic patterns and complexity in myths
- **Requirements**: Myth data, spaCy and NLTK
- **Outputs**: Structural evolution plots, complexity metrics

## File Structure

```
project/
├── data/
│   ├── json/main_loop/task_order/
│   │   ├── game.json
│   │   ├── myth.json
│   │   ├── game,myth.json
│   │   └── myth,game.json
│   └── plots/task_order/
│       ├── game/
│       ├── myth/
│       ├── game,myth/
│       └── myth,game/
├── analyses_clean/
│   ├── *.py (analysis scripts)
│   └── run_all_analyses.ipynb
└── scripts/
    └── run_analyses_clean.sh
```

## Environment Variables

The analysis scripts use these environment variables when available:

- `ANALYSIS_INPUT_FILE`: Path to input JSON file
- `ANALYSIS_OUTPUT_DIR`: Directory for output files
- `ANALYSIS_TASK_NAME`: Name of the task/experiment
- `TOGETHER_API_KEY`: API key for Together AI (myth similarity only)

## Troubleshooting

### Missing Dependencies
```bash
# Install missing packages
pip install package_name

# For spaCy model issues
python -m spacy download en_core_web_sm
```

### File Not Found Errors
- Check that input files exist in `data/json/main_loop/task_order/`
- Verify file names match expected format: `{task_order}.json`

### Permission Errors
```bash
# Make shell script executable
chmod +x scripts/run_analyses_clean.sh
```

### API Key Issues (Myth Similarity)
```bash
# Set Together AI API key
export TOGETHER_API_KEY="your_api_key_here"
```

## Output Files

Each analysis generates different types of outputs:

- **PNG files**: Visualization plots
- **JSON files**: Detailed analysis results and data
- **Console output**: Progress updates and summary statistics

Results are organized by task order in the `data/plots/task_order/` directory structure.