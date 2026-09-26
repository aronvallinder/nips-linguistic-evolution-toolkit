# D002 — Hide names and transmit the previous partner's myth locally

- Recorded / last verified: 2026-09-15 / 2026-09-15
- Decision status: Ed's anonymity proposal followed by Aron's reported implementation; local transmission documented as the setup.
- Scope: checked ordinary eight-agent rotating trust-game conditions; not all identity/ledger or donor-game variants.
- Decision authority: Edward Hughes recommendation; Aron Vallinder implementation reports.
- Implementation status: code and June/July/September bounded final samples corroborate hidden names; previous-partner myth selection verified in code.

## Decision and rationale

Remove explicit display names from gameplay prompts and pass a partner's previous myth locally. **Explicit rationale for anonymity:** Ed wants to investigate cooperation with strangers instead of norms centered on named relationships and connects this to richer gameplay history. **Unknown:** whether that mechanism actually explains observed behavior. Local transmission is a documented design feature; do not invent a separate optimum-transmission rationale.

## Evidence

- [Slide 651](../../experiment_design_reference.md#source-slide-651), Edward Hughes, 2026-06-05T11:33:08Z, thread `AAAB84WHhCo`: anonymity proposal and research aim.
- [Slide 653](../../experiment_design_reference.md#source-slide-653), Aron Vallinder, 2026-06-08T08:57:02Z, `AAAB8_CaKhU`: names not fixed as thought; reports fixing/rerunning. [Slide 654](../../experiment_design_reference.md#source-slide-654), same day at 14:50:55Z, `AAAB8-RkV1g`: after removing names.
- [Slide 655](../../experiment_design_reference.md#source-slide-655): Aron's June 17 clarification of previous-partner myth exposure and limits on mediation claims.
- [Pairing/name code](../../../games/dyadic_pairing.py), [myth selection](../../../src/myth_writer.py), [final paths/hashes](../../design_evidence/2026-09-15/sampled_runs.json). Internal names in artifacts are not proof names were shown to agents.

## Chronology and supersession

The earlier named own-one description is superseded for these checked ordinary population runs. Intermediate named history-three runs remain distinct. July's [memory repair](001-history-and-memory.md) removes own-myth recap from the new prompt while retaining own exchanges in memory; it does not replace local partner transmission with broadcast.

## Unresolved / next evidence

Name hiding removes an explicit cue, not every possible identity inference. Pairings can repeat; myths come from the previous round's partner, who need not be the current partner or a stranger. Stable-ID/ledger controls must retain their own identities. No recovered source establishes that larger populations must outperform dyads in absolute cooperation.
