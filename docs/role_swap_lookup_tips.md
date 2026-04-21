# Analyzing Role-Swapped Trust Game Data

## Quick Reference: Querying the Enhanced JSON Structure

### Understanding the New Fields

Each round entry now contains:
```python
{
    "round": int,
    "roles": {
        "Agent_1": "investor" | "trustee",
        "Agent_2": "investor" | "trustee"
    },
    "actions": {
        "Agent_1": {"action": "sent" | "returned", "amount": float},
        "Agent_2": {"action": "sent" | "returned", "amount": float}
    },
    # ... other fields (sent, received, returned, balances, myths, etc.)
}
```

### Common Analysis Queries

#### 1. Filter rounds by agent role
```python
import json

with open('3_Trust_simulation_state.json', 'r') as f:
    data = json.load(f)

# Get all rounds where Agent_1 was the investor
agent1_as_investor = [
    round_data for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'investor'
]

# Get all rounds where Agent_2 was the trustee
agent2_as_trustee = [
    round_data for round_data in data['conversation_history']
    if round_data['roles']['Agent_2'] == 'trustee'
]
```

#### 2. Analyze behavior by role
```python
# How much did Agent_1 send when they were investor?
agent1_sends_as_investor = [
    round_data['sent'] for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'investor'
]

avg_send_as_investor = sum(agent1_sends_as_investor) / len(agent1_sends_as_investor)

# How much did Agent_1 return when they were trustee?
agent1_returns_as_trustee = [
    round_data['returned'] for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'trustee'
]

avg_return_as_trustee = sum(agent1_returns_as_trustee) / len(agent1_returns_as_trustee)
```

#### 3. Get myths written under specific role
```python
# Get all myths Agent_1 wrote as investor
agent1_investor_myths = [
    round_data['myths']['Agent_1'] 
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'investor' 
    and 'myths' in round_data
]

# Get all myths Agent_2 wrote as trustee
agent2_trustee_myths = [
    round_data['myths']['Agent_2']
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_2'] == 'trustee'
    and 'myths' in round_data
]
```

#### 4. Track role transitions
```python
# See how behavior changes when switching roles
for i in range(len(data['conversation_history']) - 1):
    current = data['conversation_history'][i]
    next_round = data['conversation_history'][i + 1]
    
    agent1_role_current = current['roles']['Agent_1']
    agent1_role_next = next_round['roles']['Agent_1']
    
    if agent1_role_current != agent1_role_next:
        print(f"Round {current['round']}: Agent_1 was {agent1_role_current}")
        print(f"Round {next_round['round']}: Agent_1 is now {agent1_role_next}")
```

#### 5. Compare performance across roles
```python
# Agent_1's total earnings as investor vs trustee
agent1_investor_earnings = sum(
    round_data['investor_payoff'] if round_data['roles']['Agent_1'] == 'investor'
    else round_data['trustee_payoff']
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'investor'
)

agent1_trustee_earnings = sum(
    round_data['trustee_payoff'] if round_data['roles']['Agent_1'] == 'trustee'
    else round_data['investor_payoff']
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'trustee'
)

print(f"Agent_1 earned ${agent1_investor_earnings} as investor")
print(f"Agent_1 earned ${agent1_trustee_earnings} as trustee")
```

#### 6. Analyze reciprocity patterns
```python
# Did agents return more when their partner had previously been generous?
for i in range(1, len(data['conversation_history'])):
    current = data['conversation_history'][i]
    previous = data['conversation_history'][i - 1]
    
    # Find who was investor in previous round
    prev_investor = [agent for agent, role in previous['roles'].items() 
                     if role == 'investor'][0]
    
    # Find who is trustee in current round
    curr_trustee = [agent for agent, role in current['roles'].items() 
                    if role == 'trustee'][0]
    
    # If same agent switched from investor to trustee
    if prev_investor == curr_trustee:
        print(f"Round {i}: {curr_trustee} was investor (sent ${previous['sent']}), "
              f"now trustee (returned ${current['returned']})")
```

### Visualization Examples

#### Plot behavior by role
```python
import matplotlib.pyplot as plt

# Separate data by agent and role
agent1_investor_sends = []
agent1_investor_rounds = []
agent1_trustee_returns = []
agent1_trustee_rounds = []

for round_data in data['conversation_history']:
    if round_data['roles']['Agent_1'] == 'investor':
        agent1_investor_sends.append(round_data['sent'])
        agent1_investor_rounds.append(round_data['round'])
    else:
        agent1_trustee_returns.append(round_data['returned'])
        agent1_trustee_rounds.append(round_data['round'])

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(agent1_investor_rounds, agent1_investor_sends, 'o-', label='Agent_1 sends (as investor)')
plt.xlabel('Round')
plt.ylabel('Amount Sent')
plt.title('Agent_1 Sending Behavior (as Investor)')

plt.subplot(1, 2, 2)
plt.plot(agent1_trustee_rounds, agent1_trustee_returns, 's-', label='Agent_1 returns (as trustee)')
plt.xlabel('Round')
plt.ylabel('Amount Returned')
plt.title('Agent_1 Returning Behavior (as Trustee)')

plt.tight_layout()
plt.show()
```

### Validating Role Swapping

#### Check that roles alternate correctly
```python
def validate_role_swapping(data):
    """Verify roles alternate each round"""
    errors = []
    
    for i in range(len(data['conversation_history']) - 1):
        current = data['conversation_history'][i]
        next_round = data['conversation_history'][i + 1]
        
        for agent in ['Agent_1', 'Agent_2']:
            current_role = current['roles'][agent]
            next_role = next_round['roles'][agent]
            
            if current_role == next_role:
                errors.append(
                    f"Error: {agent} has role '{current_role}' in both "
                    f"round {current['round']} and {next_round['round']}"
                )
    
    if errors:
        print("Validation FAILED:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Validation PASSED: All roles alternate correctly")
    
    return len(errors) == 0

# Run validation
validate_role_swapping(data)
```

### Statistical Analysis

#### Compare cooperation rates by role
```python
from scipy import stats
import numpy as np

# Agent_1's cooperation (% of endowment sent) when investor
agent1_investor_cooperation = [
    round_data['sent'] / 5.0 * 100  # Assuming endowment = 5
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_1'] == 'investor'
]

# Agent_2's cooperation when investor
agent2_investor_cooperation = [
    round_data['sent'] / 5.0 * 100
    for round_data in data['conversation_history']
    if round_data['roles']['Agent_2'] == 'investor'
]

# T-test: Do agents cooperate differently depending on who is investor?
t_stat, p_value = stats.ttest_ind(agent1_investor_cooperation, 
                                   agent2_investor_cooperation)

print(f"Agent_1 avg cooperation (as investor): {np.mean(agent1_investor_cooperation):.1f}%")
print(f"Agent_2 avg cooperation (as investor): {np.mean(agent2_investor_cooperation):.1f}%")
print(f"T-test p-value: {p_value:.4f}")
```

## Tips for Analysis

1. **Role Attribution**: Always check `roles` field before attributing actions
   - Don't assume Agent_1 is always investor
   - Use role lookup to determine who did what

2. **Action Tracking**: Use `actions` field for explicit action tracking
   - Clearer than inferring from sent/returned fields
   - Shows exactly what each agent did

3. **Myth Analysis**: Myths are stored under agent ID, not role
   - Use `roles` field to determine under which role myth was written
   - Compare myth content/themes across roles for same agent

4. **Temporal Patterns**: Look for learning effects
   - Does behavior change over time within same role?
   - Do experiences in one role affect behavior in other role?

5. **Reciprocity**: Track cross-round effects
   - How does an agent's investor behavior influence their trustee behavior?
   - Do generous investors become generous trustees?
