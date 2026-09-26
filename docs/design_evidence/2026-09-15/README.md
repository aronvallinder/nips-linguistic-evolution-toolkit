# Design-reference evidence

Collected 2026-09-15 for [the design reference](../../experiment_design_reference.md). Expanded from the initial June-focused pass to the entire deck, slide 1 through 765.

## Complete review

- [Primary-source appendix in the reference](../../experiment_design_reference.md#primary-source-appendix-comments-with-their-slide-context): all 87 threads and 38 replies paired with the full text of all 63 comment-bearing slides, original anchor quotations, authors, creation/modification dates and inspected image descriptions. Deleted replies and empty resolution events are distinguished; one unmatched anchor remains explicitly unresolved.
- [Early image descriptions](comment_image_descriptions_early.md) and [late image descriptions](comment_image_descriptions_late.md): visual context for every comment-bearing slide, including explicit notes when no raster image is present. These describe source figures, not independently reproduced results.
- [full_chronology.md](full_chronology.md): original programme, dated discussions, design changes, separate branches and unresolved questions.
- [all_slide_excerpts.md](all_slide_excerpts.md) and [all_slide_comments.json](all_slide_comments.json): all 765 native slide texts, 87 available comment threads and 38 replies, plus the one nonempty speaker note. One comment is retained without a current matching slide anchor.
- [slide_coverage.md](slide_coverage.md) and [full_coverage.json](full_coverage.json): every slide accounted for. The team screened all 662 embedded images on 39 contact sheets for design content; this is not a recalculation of their scientific results.
- [image_evidence_manifest.json](image_evidence_manifest.json): image element IDs and source-byte hashes; temporary signed image URLs omitted. Original images were inspected in temporary working files, not copied into this repository.
- [early_code_provenance.md](early_code_provenance.md) and [early_sampled_runs.json](early_sampled_runs.json): six additional older final full-state samples, with bounded code/metadata checks and explicit missing dates/slide associations.

Date labels begin with November 15, 2025; earliest recovered authored comments are January 26, 2026. File creation metadata, slide labels and comment timestamps do not establish exact historical edit or implementation dates.

## Initial focused evidence (retained)

- [slide_excerpts.md](slide_excerpts.md): readable excerpts and dated comments/replies.
- [slide_comments.json](slide_comments.json): selected source text and exact metadata from the Google Drive connection. Entire-deck retrieval returned 765 slides and 87 comment threads; this file preserves 16 selected slides and 25 threads. Current slide text is not a historical revision, and chart images were not interpreted.
- [sampled_runs.json](sampled_runs.json): allowlisted metadata and hashes from three local final full-state JSONs. Source paths are relative to the repository root. Missing fields remain explicitly missing. Do not share these summaries as completed-run datasets without their corresponding final JSONs.

## Verification

The independent reviewer checked source hashes, recorded metadata, June/July prompt differences, ten-round completeness, four dyads per round, five sender/five receiver turns per agent, and local reference links. No blocking issue remained. The source researcher separately rechecked the August 18, August 24 and September 14 meeting attributions against retrieved transcripts. Wording was corrected to avoid implying that Ed participated in the September 14 wrap-up/publication agreement after leaving the meeting.

This is a bounded provenance review, not a full batch audit or independent reproduction of scientific results. No experiment, paid inference call or settings mutation was performed.

The expanded review independently checked all six additional final hashes, metadata and complete round sequences, all-slide/comment/reply counts, image coverage totals and local links. The code reviewer confirmed the April 29 communication-to-environmental-noise change and the limits on inference from the older samples. The independent reviewer corrected wording that could have turned Ed's January research hypothesis into a required outcome. No blocking factual issues remained after correction.
