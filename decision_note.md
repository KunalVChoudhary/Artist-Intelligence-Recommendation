# Decision Note — Artist Intelligence & Recommendation

## Decision supported

Given an incomplete hirer conversation, the system should return the two most plausible artists available from the supplied dataset, explain why they match using available evidence, identify important uncertainty and trade-offs, and revise the ranking when material new information arrives.

This is decision support for an initial shortlist, not a booking decision, quality guarantee, or assessment of an artist's reliability or character.

## First-version scope

The first version focuses on the complete assessment loop:

1. Build an evidence-backed capability record for each artist.
2. Interpret each hirer conversation into structured requirements and priorities.
3. Rank the strongest two plausible artists against those requirements.
4. Ask up to two questions that could materially improve the ranking.
5. Re-rank when the supplied follow-up changes the context.

The implementation uses a small Python pipeline and a local Ollama model rather than introducing a frontend, database, web search, scraping, model training, deployment infrastructure, or external reputation signals.

## Model and execution choice

I chose local **Ollama** so the assessment could be implemented and reproduced without depending on a paid external API or requiring an API key. It also keeps portfolio material local rather than sending the supplied dataset to a third-party hosted service.

**Gemma 4 E2B** was selected as the single model for the pipeline because the assessment permits local models and the available hardware makes a small multimodal model more practical than a substantially larger model. Using one model also keeps the implementation simple and consistent across artist analysis, requirement interpretation, recommendation and re-ranking.

The model is treated as a reasoning and extraction component, not as an authority on facts. Evidence comes from the supplied dataset.

## Category-specific capability model

The three artist categories use different capability dimensions because the useful signals for a photographer, musician and video editor are not interchangeable.

- **Photographers:** subjects/use cases, visual style, composition, lighting, people direction, technical execution and deliverable orientation.
- **Musicians:** act format, roles/instrumentation, genre, acoustic/electronic character, setting, energy, language, ensemble size and setup footprint.
- **Video editors:** content domain, aspect/format, story selection and sequencing, pacing, transitions, captions, colour, music/audio treatment, motion graphics and sound design.

These dimensions are used as a structured vocabulary for capability extraction and later matching rather than as a universal score for artist quality.

## Evidence policy

A central design decision is to separate what an artist **claims** from what the supplied work **demonstrates**.

Profile information can establish a claim, but a claim is not automatically treated as demonstrated capability. Media-derived observations can be considered demonstrated only when the supplied media provides meaningful supporting evidence.

The system distinguishes between:

- **demonstrated** — supported by supplied evidence
- **claimed_only** — stated by the profile without sufficient supporting evidence
- **conflicting** — available evidence and profile information disagree
- **unknown** — the supplied information is insufficient to determine the capability

Every media-derived claim should be traceable to its source file, with timestamps used for audio/video evidence where applicable.

Confidence reflects the strength and completeness of available evidence. Missing, damaged or insufficient evidence should increase uncertainty rather than being replaced with model inference.

## Media selection

The system does not blindly process every available media item. For photographers and musicians it selects a small, evenly distributed subset so that the model receives representative evidence while keeping the local inference workload manageable.

The current implementation uses at most six evenly distributed images for photographers and six evenly distributed audio files for musicians.

The selected and skipped media are retained in the generated record so that the analysis can be traced back to the supplied dataset.

## Video boundary

The current local model integration does not provide a sufficiently reliable direct video-analysis path for this assessment. Rather than silently extracting frames or claiming that an MP4 was understood when it was not, I chose an explicit evidence-integrity boundary:

- video files are discovered and recorded as unassessed media;
- no video file is sent to Ollama;
- no video frames are extracted;
- no video-derived observation is labelled as demonstrated.

As a result, video-editor intelligence can use profile information as claim evidence, while capabilities that require video evidence remain claimed-only or unknown.

This is a scope and evidence-integrity decision, not a judgement about the quality of the artists or their video work.

## Recommendation strategy

Recommendations are made from the structured artist intelligence rather than directly matching raw profile text to a hirer conversation.

The hirer conversation is first interpreted into explicit constraints, priorities, assumptions, contradictions and unknowns. Artist capabilities are then considered in that context.

Demonstrated evidence is preferred over unsupported claims. Unknown information is not automatically treated as a negative; it affects ranking when the missing information is material to the hirer's requirement.

The system returns results before asking refinement questions. Up to two questions are selected based on whether their answers could materially change the ranking.

## Re-ranking strategy

The follow-up is handled by a separate pipeline. It uses the existing recommendation, artist intelligence and new information rather than rebuilding the entire dataset.

The updated result explains what changed and why, allowing the evaluator to distinguish an actual context-driven ranking change from an arbitrary new ranking.

## Non-goals and risks

This version deliberately does not attempt to:

- assess reliability, punctuality, professionalism, character or popularity;
- infer trustworthiness from portfolio material;
- scrape external information or identify artists;
- build a production recommendation platform;
- guarantee the correctness of model-generated interpretations;
- treat incomplete evidence as proof of absence;
- analyse video that the selected model integration cannot reliably process.

The main risks are incomplete portfolio evidence, damaged or missing media, local model limitations, and model-generated JSON or reasoning errors. These are handled through explicit uncertainty, source references, structured outputs and validation rather than unsupported inference.