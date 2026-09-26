# Coding the moral of a myth

You will read 90 short myths written by AI agents between rounds of a repeated
trust game (a sender gets $5 and may send some of it; the amount is tripled;
the receiver chooses how much to send back). For each myth, write in the
`human_label` column the behavioural rule the myth endorses:

- `be generous`: give or return a lot as a default, whatever the partner did.
- `be fair`: match the partner, rewarding generosity and answering selfishness in kind.
- `be cautious`: protect yourself, start small, and extend trust only after proof.

The full rubric, with examples and tie-breaking rules, is Arabella Sinclair's
`arabella_analyses/data/rubrics/3moral_rubric.txt`. Classify the rule the myth
presents as wise, not the actions of a single character. Always pick one label.
Use `notes` for anything unclear. The answer key is not in the repository.

When done, run:
`python3 analyses/moral_validation.py --score <path to your filled sheet>`
