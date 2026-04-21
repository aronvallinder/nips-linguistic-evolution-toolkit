#!/bin/bash
# Unified Analysis Script
# 
# Usage: 
#   ./run_all_analyses.sh -all <input_json> <output_dir> [task_name]
#   ./run_all_analyses.sh -a <analyses> <input_json> <output_dir> [task_name]
#
# Examples:
#   ./run_all_analyses.sh -all data/json/model_comparison/file.json data/plots/output
#   ./run_all_analyses.sh -a ngram data/json/model_comparison/file.json data/plots/output
#   ./run_all_analyses.sh -a cooperativity,trajectory,ngram data/json/model_comparison/file.json data/plots/output
#
# Available analyses:
#   cooperativity  - Cooperativity analysis
#   trajectory     - Trajectory plotting
#   similarity     - Myth similarity (LLM-based)
#   plot_similarity - Plot myth similarity results
#   embedding      - Myth similarity embedding
#   wordchain      - Word chain evolution
#   ngram          - N-gram sentence structure
#   reciprocity    - Reciprocity analysis (trust game)
#
# Arguments:
#   -all           Run all analyses
#   -a <analyses>  Run specific analyses (comma-separated)
#   input_json     Path to the simulation JSON file
#   output_dir     Directory where plots and results will be saved
#   task_name      Optional task name (default: game_myth)

set -euo pipefail

# Get script directory to find analyses_clean
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to run a specific analysis
run_analysis() {
    local name="$1"
    case "$name" in
        cooperativity)
            echo "Running Cooperativity Analysis..."
            python "$PROJECT_ROOT/analyses_clean/cooperativity_analysis.py"
            ;;
        trajectory)
            echo "Running Trajectory Plotting..."
            python "$PROJECT_ROOT/analyses_clean/trajectory_plotting.py"
            ;;
        similarity)
            echo "Running Myth Similarity Analysis..."
            python "$PROJECT_ROOT/analyses_clean/myth_similarity.py"
            ;;
        plot_similarity)
            echo "Running Plot Myth Similarity..."
            python "$PROJECT_ROOT/analyses_clean/plot_myth_similarity.py"
            ;;
        embedding)
            echo "Running Myth Similarity Embedding..."
            python "$PROJECT_ROOT/analyses_clean/myth_similarity_embedding.py"
            ;;
        wordchain)
            echo "Running Word Chain Evolution..."
            python "$PROJECT_ROOT/analyses_clean/word_chain_evolution.py"
            ;;
        ngram)
            echo "Running N-gram Sentence Structure..."
            python "$PROJECT_ROOT/analyses_clean/n_gram_sentence_structure.py"
            ;;
        reciprocity)
            echo "Running Reciprocity Analysis..."
            python "$PROJECT_ROOT/analyses_clean/reciprocity_analysis.py" "$ANALYSIS_INPUT_FILE" "$ANALYSIS_OUTPUT_DIR"
            ;;
        *)
            echo "Error: Unknown analysis '$name'"
            echo "Available: cooperativity, trajectory, similarity, plot_similarity, embedding, wordchain, ngram, reciprocity"
            exit 1
            ;;
    esac
}

# Show usage
show_usage() {
    echo "Usage:"
    echo "  $0 -all <input_json> <output_dir> [task_name]"
    echo "  $0 -a <analyses> <input_json> <output_dir> [task_name]"
    echo ""
    echo "Available analyses (comma-separated for -a):"
    echo "  cooperativity, trajectory, similarity, plot_similarity, embedding, wordchain, ngram, reciprocity"
    echo ""
    echo "Examples:"
    echo "  $0 -all data/json/model_comparison/file.json data/plots/output"
    echo "  $0 -a ngram data/json/model_comparison/file.json data/plots/output"
    echo "  $0 -a cooperativity,trajectory data/json/model_comparison/file.json data/plots/output"
    exit 1
}

# Check minimum arguments
if [ $# -lt 3 ]; then
    show_usage
fi

# Parse flag
FLAG="$1"
shift

if [ "$FLAG" == "-all" ]; then
    ANALYSES="cooperativity,trajectory,similarity,plot_similarity,embedding,wordchain,ngram,reciprocity"
    INPUT_FILE="$1"
    OUTPUT_DIR="$2"
    TASK_NAME="${3:-game_myth}"
elif [ "$FLAG" == "-a" ]; then
    ANALYSES="$1"
    shift
    INPUT_FILE="$1"
    OUTPUT_DIR="$2"
    TASK_NAME="${3:-game_myth}"
else
    echo "Error: First argument must be -all or -a"
    show_usage
fi

# Validate input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found!"
    exit 1
fi

# Export environment variables for Python scripts
export ANALYSIS_INPUT_FILE="$INPUT_FILE"
export ANALYSIS_OUTPUT_DIR="$OUTPUT_DIR"
export ANALYSIS_TASK_NAME="$TASK_NAME"
export TOGETHER_API_KEY="${TOGETHER_API_KEY:-4f0440e2cc8baa37f8017270d398124bd4e477459f3500c74290591509b2e6b3}"  # Use existing env var if set

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "Running Analyses"
echo "========================================"
echo "Input:    $INPUT_FILE"
echo "Output:   $OUTPUT_DIR"
echo "Task:     $TASK_NAME"
echo "Analyses: $ANALYSES"
echo "========================================"
echo ""

# Run selected analyses
IFS=',' read -ra ANALYSIS_ARRAY <<< "$ANALYSES"
TOTAL=${#ANALYSIS_ARRAY[@]}
COUNT=1

for analysis in "${ANALYSIS_ARRAY[@]}"; do
    echo "[$COUNT/$TOTAL] "
    run_analysis "$analysis"
    echo ""
    ((COUNT++))
done

echo "========================================"
echo "Analyses complete!"
echo "Outputs saved to: $OUTPUT_DIR"
echo "========================================"
