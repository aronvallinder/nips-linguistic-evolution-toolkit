"""
Trajectory plotting.
"""

import json
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for saving plots (avoids GUI backend issues)
import matplotlib.pyplot as plt
import numpy as np
import os
from typing import Dict, List, Tuple
from pathlib import Path

def load_simulation_data(filepath: str) -> Dict:
    """Load simulation state from JSON file"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_trajectory_metrics(conversation_history: List[Dict]) -> Dict:
    """Calculate metrics to identify interesting trajectories"""
    def _require_metric(r: Dict, key: str) -> float:
        if key not in r:
            raise KeyError(f"Missing key '{key}' in conversation_history (round={r['round']}). Wrong JSON/schema?")
        if r[key] is None:
            raise ValueError(
                f"Key '{key}' is null in conversation_history (round={r['round']}). "
                "This looks like a myth-only JSON; do not run trajectory analysis on myth-only."
            )
        return float(r[key])

    metrics = {
        "sent_variance": np.var([_require_metric(r, "sent") for r in conversation_history]),
        "returned_variance": np.var([_require_metric(r, "returned") for r in conversation_history]),
        "investor_payoff_variance": np.var([_require_metric(r, "investor_payoff") for r in conversation_history]),
        "trustee_payoff_variance": np.var([_require_metric(r, "trustee_payoff") for r in conversation_history]),
        "total_variance": 0,
        "cooperation_score": 0,  # Average return ratio
        "trust_score": 0,  # Average send ratio
        "final_balance_diff": 0,
    }

    if conversation_history:
        sent_values = [_require_metric(r, "sent") for r in conversation_history]
        returned_values = [_require_metric(r, "returned") for r in conversation_history]
        received_values = [_require_metric(r, "received") for r in conversation_history]

        # Calculate cooperation (return ratio)
        return_ratios = [ret / rec if rec > 0 else 0 for ret, rec in zip(returned_values, received_values)]
        metrics["cooperation_score"] = np.mean(return_ratios)

        # Calculate trust (send ratio of endowment)
        endowment = _require_metric(conversation_history[0], "sent") + _require_metric(conversation_history[0], "investor_payoff")
        if endowment > 0:
            send_ratios = [s / endowment for s in sent_values]
            metrics["trust_score"] = np.mean(send_ratios)

        # Final balance difference
        if "balances" in conversation_history[-1]:
            balances = conversation_history[-1]["balances"]
            if "Agent_1" in balances and "Agent_2" in balances:
                metrics["final_balance_diff"] = abs(balances["Agent_1"] - balances["Agent_2"])

        # Total variance (sum of all variances)
        metrics["total_variance"] = (
            metrics["sent_variance"]
            + metrics["returned_variance"]
            + metrics["investor_payoff_variance"]
            + metrics["trustee_payoff_variance"]
        )

    return metrics


def identify_interesting_trajectories(
    filepath: str, top_n: int = 3, criteria: str = "variance"
) -> List[Tuple[Dict, Dict]]:
    """
    Identify interesting trajectories based on various criteria

    Args:
        filepath: Path to simulation JSON file
        top_n: Number of interesting trajectories to return
        criteria: 'variance', 'cooperation', 'trust', 'balance_diff', or 'all'

    Returns:
        List of (trajectory_data, metrics) tuples
    """
    data = load_simulation_data(filepath)
    conversation_history = data.get("conversation_history", [])

    if not conversation_history:
        return []

    # Calculate metrics for this trajectory
    metrics = calculate_trajectory_metrics(conversation_history)

    # For now, return single trajectory (you can extend to compare multiple files)
    return [(conversation_history, metrics)]


def plot_numerical_trajectories(
    conversation_history: List[Dict], save_path: str = None, title: str = "Trust Game Trajectory"
):
    """
    Create comprehensive plots of numerical choices over rounds

    Args:
        conversation_history: List of round data dictionaries
        save_path: Optional path to save the figure
        title: Title for the plot
    """
    if not conversation_history:
        print("No conversation history to plot")
        return

    rounds = [r["round"] for r in conversation_history]
    min_round = min(rounds) if rounds else 1
    max_round = max(rounds) if rounds else 1
    num_rounds = max_round - min_round + 1

    def compute_tick_step(n: int) -> int:
        """
        Choose a readable tick spacing based on number of rounds.
        Examples:
        - ~50 rounds  -> every 10
        - ~200 rounds -> every 20
        - ~600 rounds -> every 50
        """
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

    tick_step = compute_tick_step(num_rounds)
    # Use the actual first round as the left anchor so plots don't show a spurious 0 tick/limit.
    xlim_left = min_round
    xticks = list(range(min_round, max_round + 1, tick_step))
    if xticks and xticks[-1] != max_round:
        xticks.append(max_round)

    # Extract role information to determine which agent had which role each round
    investor_agent_per_round: List[str] = []
    trustee_agent_per_round: List[str] = []
    for r in conversation_history:
        roles = r.get("roles", {})
        # Find which agent is investor and which is trustee
        investor_agent = None
        trustee_agent = None
        for agent_id, role in roles.items():
            if role == "investor":
                investor_agent = agent_id
            elif role == "trustee":
                trustee_agent = agent_id
        investor_agent_per_round.append(investor_agent)
        trustee_agent_per_round.append(trustee_agent)

    def require_value(r: Dict, key: str, round_num: int):
        if key not in r:
            raise KeyError(f"Missing key '{key}' in round {round_num}. Wrong JSON/schema?")
        v = r[key]
        if v is None:
            raise ValueError(
                f"Key '{key}' is null in round {round_num}. "
                "This looks like a myth-only JSON (game fields are null). "
                "Do not run trajectory plotting on myth-only."
            )
        return v

    # Extract numerical data
    # Guard early: catches myth-only immediately with a clear message.
    if conversation_history:
        rn0 = conversation_history[0]["round"]
        for k in ["sent", "received", "returned", "investor_payoff", "trustee_payoff", "balances", "actions"]:
            require_value(conversation_history[0], k, rn0)

    sent = [float(require_value(r, "sent", r["round"])) for r in conversation_history]
    received = [float(require_value(r, "received", r["round"])) for r in conversation_history]
    returned = [float(require_value(r, "returned", r["round"])) for r in conversation_history]
    investor_payoff = [float(require_value(r, "investor_payoff", r["round"])) for r in conversation_history]
    trustee_payoff = [float(require_value(r, "trustee_payoff", r["round"])) for r in conversation_history]

    # Extract balances
    agent_1_balance: List[float] = []
    agent_2_balance: List[float] = []
    for r in conversation_history:
        rn = r["round"]
        balances = require_value(r, "balances", rn)  # raises if missing/null
        if not isinstance(balances, dict):
            raise TypeError(f"'balances' is not an object in round {rn}: got {type(balances).__name__}")
        if "Agent_1" not in balances or "Agent_2" not in balances:
            raise KeyError(f"Missing Agent_1/Agent_2 in balances for round {rn}: keys={list(balances.keys())}")
        agent_1_balance.append(float(balances["Agent_1"]))
        agent_2_balance.append(float(balances["Agent_2"]))

    # Extract balances by role (whoever is investor/trustee in that round)
    investor_role_balance: List[float] = []
    trustee_role_balance: List[float] = []
    for i, r in enumerate(conversation_history):
        rn = r["round"]
        balances = require_value(r, "balances", rn)
        if not isinstance(balances, dict):
            raise TypeError(f"'balances' is not an object in round {rn}: got {type(balances).__name__}")
        investor_agent = investor_agent_per_round[i]
        trustee_agent = trustee_agent_per_round[i]
        if investor_agent is None or trustee_agent is None:
            raise ValueError(f"Missing role assignment in round {rn}: investor={investor_agent} trustee={trustee_agent}")
        if investor_agent not in balances or trustee_agent not in balances:
            raise KeyError(
                f"Missing investor/trustee balance key(s) in round {rn}: "
                f"investor_agent={investor_agent} trustee_agent={trustee_agent} keys={list(balances.keys())}"
            )
        investor_role_balance.append(float(balances[investor_agent]))
        trustee_role_balance.append(float(balances[trustee_agent]))

    # Helper function to plot line with agent-specific markers
    def plot_with_agent_markers(ax, rounds, values, label, color, agent_per_round, linewidth=2):
        """Plot a line and overlay markers based on which agent had the role"""
        # Plot the line first
        if color:
            line = ax.plot(rounds, values, label=label, linewidth=linewidth, color=color)
            line_color = line[0].get_color()
        else:
            line = ax.plot(rounds, values, label=label, linewidth=linewidth)
            line_color = line[0].get_color()

        # Overlay markers: 'o' for Agent_1, '^' for Agent_2
        agent_1_marker_count = 0
        agent_2_marker_count = 0
        none_marker_count = 0
        for i, agent in enumerate(agent_per_round):
            if agent:  # Only plot marker if agent is not None
                marker = "o" if agent == "Agent_1" else "^"
                ax.scatter(rounds[i], values[i], marker=marker, color=line_color, s=50, zorder=5)
                if agent == "Agent_1":
                    agent_1_marker_count += 1
                else:
                    agent_2_marker_count += 1
            else:
                none_marker_count += 1

    def plot_agent_balance_with_role_markers(
        ax,
        rounds: List[int],
        values: List[float],
        label: str,
        color: str,
        agent_id: str,
        investor_agent_per_round: List[str],
        trustee_agent_per_round: List[str],
        linewidth: int = 2,
    ):
        """
        Plot an agent's cumulative balance line, with markers encoding ROLE per round:
        - '^' triangle for investor
        - 'o' ball for trustee
        """
        line = ax.plot(rounds, values, label=label, linewidth=linewidth, color=color)
        line_color = line[0].get_color()

        investor_marker_count = 0
        trustee_marker_count = 0
        unknown_marker_count = 0

        for i in range(len(rounds)):
            is_investor = investor_agent_per_round[i] == agent_id
            is_trustee = trustee_agent_per_round[i] == agent_id

            if is_investor:
                marker = "^"
                investor_marker_count += 1
            elif is_trustee:
                marker = "o"
                trustee_marker_count += 1
            else:
                marker = "x"
                unknown_marker_count += 1

            ax.scatter(rounds[i], values[i], marker=marker, color=line_color, s=50, zorder=5)

    def plot_role_balance_with_agent_markers(
        ax,
        rounds: List[int],
        values: List[float],
        label: str,
        color: str,
        agent_per_round: List[str],
        linewidth: int = 2,
    ):
        """
        Plot a role's cumulative balance line, with markers encoding AGENT per round:
        - '^' triangle for Agent_1 (Agent A)
        - 'o' ball for Agent_2 (Agent B)
        """
        line = ax.plot(rounds, values, label=label, linewidth=linewidth, color=color)
        line_color = line[0].get_color()

        agent_1_marker_count = 0
        agent_2_marker_count = 0
        unknown_marker_count = 0

        for i, agent in enumerate(agent_per_round):
            if agent == "Agent_1":
                marker = "^"
                agent_1_marker_count += 1
            elif agent == "Agent_2":
                marker = "o"
                agent_2_marker_count += 1
            else:
                marker = "x"
                unknown_marker_count += 1

            ax.scatter(rounds[i], values[i], marker=marker, color=line_color, s=50, zorder=5)

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(title, fontsize=16, fontweight="bold")

    # Plot 1: Transaction amounts (sent, received, returned)
    ax1 = axes[0, 0]
    # Sent: marker based on which agent is investor (who sends)
    plot_with_agent_markers(ax1, rounds, sent, "Sent", None, investor_agent_per_round)
    # Received: marker based on which agent is trustee (who receives)
    plot_with_agent_markers(ax1, rounds, received, "Received", None, trustee_agent_per_round)
    # Returned: marker based on which agent is trustee (who returns)
    plot_with_agent_markers(ax1, rounds, returned, "Returned", None, trustee_agent_per_round)
    ax1.set_xlabel("Round", fontsize=12)
    ax1.set_ylabel("Amount", fontsize=12)
    ax1.set_title("Transaction Flow", fontsize=14, fontweight="bold")
    ax1.legend(loc="best")
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(xticks)
    ax1.set_xlim(xlim_left, max_round)
    ax1.set_ylim(bottom=0)

    # Plot 2: Payoffs per round
    ax2 = axes[0, 1]
    # Investor Payoff: marker based on which agent is investor
    plot_with_agent_markers(ax2, rounds, investor_payoff, "Investor Payoff", "green", investor_agent_per_round)
    # Trustee Payoff: marker based on which agent is trustee
    plot_with_agent_markers(ax2, rounds, trustee_payoff, "Trustee Payoff", "orange", trustee_agent_per_round)
    ax2.set_xlabel("Round", fontsize=12)
    ax2.set_ylabel("Payoff", fontsize=12)
    ax2.set_title("Payoffs per Round", fontsize=14, fontweight="bold")
    ax2.legend(loc="best")
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(xticks)
    ax2.set_xlim(xlim_left, max_round)
    ax2.set_ylim(bottom=0)

    # Plot 3: Cumulative balances (Agents)
    ax3 = axes[1, 0]
    plot_agent_balance_with_role_markers(
        ax3,
        rounds,
        agent_1_balance,
        "Agent_1 Balance",
        "blue",
        "Agent_1",
        investor_agent_per_round,
        trustee_agent_per_round,
    )
    plot_agent_balance_with_role_markers(
        ax3,
        rounds,
        agent_2_balance,
        "Agent_2 Balance",
        "red",
        "Agent_2",
        investor_agent_per_round,
        trustee_agent_per_round,
    )
    ax3.set_xlabel("Round", fontsize=12)
    ax3.set_ylabel("Cumulative Balance", fontsize=12)
    ax3.set_title("Cumulative Balances (Agents)", fontsize=14, fontweight="bold")
    # Add figures in legend: role markers
    legend_line_handles, legend_line_labels = ax3.get_legend_handles_labels()
    role_marker_handles = [
        plt.Line2D([], [], marker="^", linestyle="None", color="gray", markersize=8, label="Investor (^)"),
        plt.Line2D([], [], marker="o", linestyle="None", color="gray", markersize=8, label="Trustee (o)"),
    ]
    ax3.legend(handles=legend_line_handles + role_marker_handles, labels=legend_line_labels + ["Investor (^)", "Trustee (o)"], loc="best")
    ax3.grid(True, alpha=0.3)
    ax3.set_xticks(xticks)
    ax3.set_xlim(xlim_left, max_round)
    ax3.set_ylim(bottom=0)

    # Plot 4: Cumulative balances (Roles)
    ax4 = axes[1, 1]
    plot_role_balance_with_agent_markers(
        ax4,
        rounds,
        investor_role_balance,
        "Investor Role Balance",
        "blue",
        investor_agent_per_round,
    )
    plot_role_balance_with_agent_markers(
        ax4,
        rounds,
        trustee_role_balance,
        "Trustee Role Balance",
        "red",
        trustee_agent_per_round,
    )
    ax4.set_xlabel("Round", fontsize=12)
    ax4.set_ylabel("Cumulative Balance", fontsize=12)
    ax4.set_title("Cumulative Balances (Roles)", fontsize=14, fontweight="bold")
    # Add figures in legend: agent markers (Agent A/B)
    legend_line_handles, legend_line_labels = ax4.get_legend_handles_labels()
    agent_marker_handles = [
        plt.Line2D([], [], marker="^", linestyle="None", color="gray", markersize=8, label="Agent_1 (^)"),
        plt.Line2D([], [], marker="o", linestyle="None", color="gray", markersize=8, label="Agent_2 (o)"),
    ]
    ax4.legend(handles=legend_line_handles + agent_marker_handles, labels=legend_line_labels + ["Agent_1 (^)", "Agent_2 (o)"], loc="best")
    ax4.grid(True, alpha=0.3)
    ax4.set_xticks(xticks)
    ax4.set_xlim(xlim_left, max_round)
    ax4.set_ylim(bottom=0)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved trajectory plot to {save_path}")
    else:
        plt.show()

    plt.close()


def display_raw_text_trajectory(conversation_history: List[Dict], agent_id: str = None, max_rounds: int = 5):
    """
    Display raw text (myths) for a trajectory

    Args:
        conversation_history: List of round data dictionaries
        agent_id: Specific agent to show (None for both)
        max_rounds: Maximum number of rounds to display
    """
    print("\n" + "=" * 80)
    print("RAW TEXT TRAJECTORY (MYTHS)")
    print("=" * 80)

    rounds_to_show = conversation_history[:max_rounds]

    for round_data in rounds_to_show:
        round_num = round_data.get("round", "?")
        myths = round_data.get("myths", {})

        print(f"\n{'='*80}")
        print(f"ROUND {round_num}")
        print(f"{'='*80}")

        # Display numerical summary
        print("\nNumerical Summary:")
        print(f"  Sent: {round_data.get('sent', 0)}")
        print(f"  Received: {round_data.get('received', 0)}")
        print(f"  Returned: {round_data.get('returned', 0)}")
        print(f"  Investor Payoff: {round_data.get('investor_payoff', 0)}")
        print(f"  Trustee Payoff: {round_data.get('trustee_payoff', 0)}")

        # Display myths
        print(f"\n{'─'*80}")
        print("MYTHS:")
        print(f"{'─'*80}")

        if agent_id and agent_id in myths:
            print(f"\n{agent_id}:")
            print(f"{'─'*40}")
            print(myths[agent_id])
        else:
            for agent, myth_text in myths.items():
                print(f"\n{agent}:")
                print(f"{'─'*40}")
                print(myth_text)
                print()


def analyze_interesting_trajectories(filepath: str, output_dir: str, top_n: int = 3):
    """
    Complete analysis: identify, visualize, and display interesting trajectories

    Args:
        filepath: Path to simulation JSON file
        output_dir: Directory to save plots
        top_n: Number of trajectories to analyze
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Identify interesting trajectories
    trajectories = identify_interesting_trajectories(filepath, top_n=top_n)

    if not trajectories:
        print("No trajectories found")
        return

    for idx, (conversation_history, metrics) in enumerate(trajectories):
        print(f"\n{'='*80}")
        print(f"TRAJECTORY {idx + 1}")
        print(f"{'='*80}")

        # Print metrics
        print("\nTrajectory Metrics:")
        print(f"  Total Variance: {metrics['total_variance']:.2f}")
        print(f"  Cooperation Score (avg return ratio): {metrics['cooperation_score']:.3f}")
        print(f"  Trust Score (avg send ratio): {metrics['trust_score']:.3f}")
        print(f"  Final Balance Difference: {metrics['final_balance_diff']:.2f}")

        # Generate plot
        plot_filename = f"{output_dir}/trajectory_{idx+1}_numerical.png"
        plot_numerical_trajectories(
            conversation_history, save_path=plot_filename, title=f"Trajectory {idx+1} - Numerical Choices"
        )

        # Display raw text
        display_raw_text_trajectory(conversation_history, max_rounds=10)

    print(f"\n{'='*80}")
    print("Analysis complete!")
    print(f"file saved to {output_dir}")
    print(f"{'='*80}")


def main():
    """Main function to run trajectory analysis"""
    analyze_interesting_trajectories(filepath=input_filepath, output_dir=output_dir, top_n=number_of_trajectories)


if __name__ == "__main__":
    # Check if running from shell script (environment variables available)
    input_filepath = os.environ.get(
        "ANALYSIS_INPUT_FILE",
        "/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json",
    )
    output_dir = os.environ.get(
        "ANALYSIS_OUTPUT_DIR",
        "/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini/trajectory_plotting",
    )
    task_name = os.environ.get("ANALYSIS_TASK_NAME", "game_myth")
    number_of_trajectories = 1

    main()

