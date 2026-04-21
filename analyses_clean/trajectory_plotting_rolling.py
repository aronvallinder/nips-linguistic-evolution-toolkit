"""
Trajectory Plotting with Rolling Averages
For high round counts (500+), uses smoothed lines instead of raw data points.
"""

import json
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, List
from pathlib import Path

def load_simulation_data(filepath: str) -> Dict:
    """Load simulation state from JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def rolling_average(values: List[float], window: int = 20) -> np.ndarray:
    """
    Calculate rolling average with edge handling.
    
    Args:
        values: List of values to smooth
        window: Window size for rolling average
    
    Returns:
        Smoothed numpy array
    """
    arr = np.array(values, dtype=float)
    if len(arr) < window:
        return arr
    
    kernel = np.ones(window) / window
    smoothed = np.convolve(arr, kernel, mode='same')
    
    # Fix edge effects by using smaller windows at edges
    half_window = window // 2
    for i in range(half_window):
        smoothed[i] = np.mean(arr[:i + half_window + 1])
        smoothed[-(i + 1)] = np.mean(arr[-(i + half_window + 1):])
    
    return smoothed


def compute_window_size(num_rounds: int) -> int:
    """
    Auto-compute appropriate window size based on number of rounds.
    
    Args:
        num_rounds: Total number of rounds in data
    
    Returns:
        Recommended window size
    """
    if num_rounds <= 50:
        return 5
    if num_rounds <= 200:
        return 10
    if num_rounds <= 500:
        return 20
    if num_rounds <= 1000:
        return 40
    return 50


def compute_tick_step(n: int) -> int:
    """Choose a readable tick spacing based on number of rounds."""
    # Small runs should have dense ticks; otherwise you get 0,10,15 for a 15-round run.
    if n <= 20:
        return 1
    if n <= 60:
        return 5
    if n <= 250:
        return 20
    if n <= 700:
        return 50
    if n <= 1500:
        return 100
    return 200


def plot_numerical_trajectories(conversation_history: List[Dict],
                                 save_path: str = None,
                                 title: str = "Trust Game Trajectory",
                                 window: int = None,
                                 show_raw: bool = True):
    """
    Create trajectory plots with rolling averages for readability at high round counts.
    
    Args:
        conversation_history: List of round data dictionaries
        save_path: Optional path to save the figure
        title: Title for the plot
        window: Rolling average window size (auto-computed if None)
        show_raw: Whether to show faint raw data trace underneath
    """
    if not conversation_history:
        print("No conversation history to plot")
        return

    # Many datasets (e.g., myth-only phases) may store game fields as null.
    # Rolling plot expects game numeric fields; filter to valid game rounds.
    invalid_round_samples = []
    invalid_count = 0
    for r in conversation_history:
        b = r.get("balances")
        is_balances_dict = isinstance(b, dict)
        has_numeric_game = (
            r.get("sent") is not None
            and r.get("received") is not None
            and r.get("returned") is not None
            and r.get("investor_payoff") is not None
            and r.get("trustee_payoff") is not None
        )
        if not (is_balances_dict and has_numeric_game):
            invalid_count += 1
            if len(invalid_round_samples) < 5:
                invalid_round_samples.append(
                    {
                        "round": r.get("round"),
                        "balances_type": type(b).__name__,
                        "sent": r.get("sent"),
                        "received": r.get("received"),
                        "returned": r.get("returned"),
                        "investor_payoff": r.get("investor_payoff"),
                        "trustee_payoff": r.get("trustee_payoff"),
                        "has_roles": "roles" in r,
                    }
                )

    filtered_conversation_history = [
        r
        for r in conversation_history
        if isinstance(r.get("balances"), dict)
        and r.get("sent") is not None
        and r.get("received") is not None
        and r.get("returned") is not None
        and r.get("investor_payoff") is not None
        and r.get("trustee_payoff") is not None
    ]

    if not filtered_conversation_history:
        print("No valid game rounds found (game fields missing or null).")
        return

    conversation_history = filtered_conversation_history

    rounds = [r['round'] for r in conversation_history]
    min_round = min(rounds) if rounds else 1
    max_round = max(rounds) if rounds else 1
    num_rounds = max_round - min_round + 1

    # Auto-compute window if not provided
    if window is None:
        window = compute_window_size(num_rounds)

    tick_step = compute_tick_step(num_rounds)
    # Use the actual first round as the left anchor so plots don't show a spurious 0 tick/limit.
    xlim_left = min_round
    xticks = list(range(min_round, max_round + 1, tick_step))
    if xticks and xticks[-1] != max_round:
        xticks.append(max_round)

    # Extract numerical data
    sent = [r.get('sent', 0) for r in conversation_history]
    received = [r.get('received', 0) for r in conversation_history]
    returned = [r.get('returned', 0) for r in conversation_history]
    investor_payoff = [r.get('investor_payoff', 0) for r in conversation_history]
    trustee_payoff = [r.get('trustee_payoff', 0) for r in conversation_history]

    # Extract balances (NOTE: these are agent balances, not role balances)
    agent_1_balance = []
    agent_2_balance = []
    for r in conversation_history:
        balances = r.get('balances', {})
        agent_1_balance.append(balances.get('Agent_1', 0))
        agent_2_balance.append(balances.get('Agent_2', 0))

    # Calculate ratios
    return_ratios = [ret / rec if rec > 0 else 0
                    for ret, rec in zip(returned, received)]
    endowment = sent[0] + investor_payoff[0] if len(sent) > 0 else 10
    trust_ratios = [s / endowment if endowment > 0 else 0 for s in sent]

    # Compute rolling averages
    sent_smooth = rolling_average(sent, window)
    received_smooth = rolling_average(received, window)
    returned_smooth = rolling_average(returned, window)
    investor_payoff_smooth = rolling_average(investor_payoff, window)
    trustee_payoff_smooth = rolling_average(trustee_payoff, window)
    agent_1_balance_smooth = rolling_average(agent_1_balance, window)
    agent_2_balance_smooth = rolling_average(agent_2_balance, window)
    return_ratios_smooth = rolling_average(return_ratios, window)
    trust_ratios_smooth = rolling_average(trust_ratios, window)

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"{title}\n(Rolling average, window={window})", fontsize=16, fontweight='bold')

    raw_alpha = 0.15 if show_raw else 0

    # Plot 1: Transaction amounts
    ax1 = axes[0, 0]
    if show_raw:
        ax1.plot(rounds, sent, color='C0', alpha=raw_alpha, linewidth=0.5)
        ax1.plot(rounds, received, color='C1', alpha=raw_alpha, linewidth=0.5)
        ax1.plot(rounds, returned, color='C2', alpha=raw_alpha, linewidth=0.5)
    ax1.plot(rounds, sent_smooth, color='C0', linewidth=2.5, label='Sent')
    ax1.plot(rounds, received_smooth, color='C1', linewidth=2.5, label='Received')
    ax1.plot(rounds, returned_smooth, color='C2', linewidth=2.5, label='Returned')
    ax1.set_xlabel('Round', fontsize=12)
    ax1.set_ylabel('Amount', fontsize=12)
    ax1.set_title('Transaction Flow', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(xticks)
    ax1.set_xlim(xlim_left, max_round)
    ax1.set_ylim(bottom=0)

    # Plot 2: Payoffs per round
    ax2 = axes[0, 1]
    if show_raw:
        ax2.plot(rounds, investor_payoff, color='green', alpha=raw_alpha, linewidth=0.5)
        ax2.plot(rounds, trustee_payoff, color='orange', alpha=raw_alpha, linewidth=0.5)
    ax2.plot(rounds, investor_payoff_smooth, color='green', linewidth=2.5, label='Investor Payoff')
    ax2.plot(rounds, trustee_payoff_smooth, color='orange', linewidth=2.5, label='Trustee Payoff')
    ax2.set_xlabel('Round', fontsize=12)
    ax2.set_ylabel('Payoff', fontsize=12)
    ax2.set_title('Payoffs per Round', fontsize=14, fontweight='bold')
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(xticks)
    ax2.set_xlim(xlim_left, max_round)
    ax2.set_ylim(bottom=0)

    # Plot 3: Cumulative balances
    ax3 = axes[1, 0]
    if show_raw:
        ax3.plot(rounds, agent_1_balance, color='blue', alpha=raw_alpha, linewidth=0.5)
        ax3.plot(rounds, agent_2_balance, color='red', alpha=raw_alpha, linewidth=0.5)
    ax3.plot(rounds, agent_1_balance_smooth, color='blue', linewidth=2.5, label='Agent_1 Balance')
    ax3.plot(rounds, agent_2_balance_smooth, color='red', linewidth=2.5, label='Agent_2 Balance')
    ax3.set_xlabel('Round', fontsize=12)
    ax3.set_ylabel('Cumulative Balance', fontsize=12)
    ax3.set_title('Cumulative Balances', fontsize=14, fontweight='bold')
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(xticks)
    ax3.set_xlim(xlim_left, max_round)
    ax3.set_ylim(bottom=0)

    # Plot 4: Ratios
    ax4 = axes[1, 1]
    if show_raw:
        ax4.plot(rounds, return_ratios, color='purple', alpha=raw_alpha, linewidth=0.5)
        ax4.plot(rounds, trust_ratios, color='brown', alpha=raw_alpha, linewidth=0.5)
    ax4.plot(rounds, return_ratios_smooth, color='purple', linewidth=2.5, label='Return Ratio')
    ax4.plot(rounds, trust_ratios_smooth, color='brown', linewidth=2.5, label='Trust Ratio (Send/Endowment)')
    ax4.set_xlabel('Round', fontsize=12)
    ax4.set_ylabel('Ratio', fontsize=12)
    ax4.set_title('Cooperation & Trust Ratios', fontsize=14, fontweight='bold')
    ax4.legend(loc='best')
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1.1)
    ax4.set_xticks(xticks)
    ax4.set_xlim(xlim_left, max_round)
    ax4.axhline(y=1.0, color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved trajectory plot to {save_path}")
    else:
        plt.show()

    plt.close()


def analyze_trajectory(filepath: str, output_dir: str):
    """
    Analyze and plot trajectory from simulation file.
    
    Args:
        filepath: Path to simulation JSON file
        output_dir: Directory to save plots
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    data = load_simulation_data(filepath)
    conversation_history = data.get('conversation_history', [])

    if not conversation_history:
        print("No conversation history found")
        return

    print(f"Loaded {len(conversation_history)} rounds")

    plot_filename = f"{output_dir}/trajectory_rolling.png"
    plot_numerical_trajectories(
        conversation_history,
        save_path=plot_filename,
        title="Trust Game Trajectory"
    )

    print(f"Analysis complete! Plot saved to {plot_filename}")


def main():
    """Main function"""
    analyze_trajectory(
        filepath=input_filepath,
        output_dir=output_dir
    )


if __name__ == "__main__":
    input_filepath = os.environ.get(
        'ANALYSIS_INPUT_FILE',
        '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/pilot/pilot_000_llama-3.1-8b-instruct_neutral_myth_game.json'
    )
    output_dir = os.environ.get(
        'ANALYSIS_OUTPUT_DIR',
        '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/pilot/llama-3.1-8b-instruct_neutral_game_myth'
    )

    main()
