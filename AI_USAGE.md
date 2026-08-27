# AI Usage

AI coding assistance was used extensively during development. I used both **OpenAI Codex** and ChatGPT for code generation, implementation guidance, debugging, refactoring, prompt design, schema design, documentation, and code review.

## How AI was used

### Development assistance

Codex was used to generate and refine substantial portions of the Python implementation, including:

- Ollama client integration
- Artist profile and media processing
- Category-specific prompt construction
- Recommendation and re-ranking pipelines
- JSON parsing and output handling
- Error handling and project structure

ChatGPT was used alongside Codex to reason about the assessment requirements, review implementation choices, refine prompts and schemas, and identify potential issues in the code.

### Design and reasoning

AI assistance was used to explore and refine:

- Category-specific capability schemas
- Evidence and confidence representation
- Hirer requirement extraction
- Recommendation and re-ranking logic
- Media-selection strategy
- Handling of incomplete or conflicting information

The final design decisions were made based on the assessment requirements and the constraints of the selected local model.

### Important implementation decision

A deliberate decision was made not to send video files to the model or extract video frames. The current implementation therefore does not make video-derived demonstrated capability claims. This was treated as an evidence-integrity and scope decision rather than presenting unanalysed video as evidence.

## Human verification and responsibility

I remain responsible for the submitted code, system design, prompts, generated outputs, and assessment claims.

In particular, I reviewed and made the final decisions regarding:

- System scope and architecture
- Category-specific schemas
- Evidence versus profile claims
- Media-selection approach
- Video-analysis limitation
- Recommendation and re-ranking flow
- Model and local Ollama approach
- Documentation and submission structure

AI-generated code and suggestions were treated as development assistance rather than independently verified ground truth. I reviewed the implementation and am responsible for understanding and defending the submitted code and decisions.