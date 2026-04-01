# AI Usage

## Tools Used

- **Claude Code (Claude Opus 4.6)** — Primary AI coding assistant used throughout the project for code generation, architecture planning, and documentation.

## Where AI Helped

1. **Architecture planning** — Used Claude to brainstorm the safety pipeline design, discuss tradeoffs between SSE vs HTTP, and evaluate the fail-open vs fail-closed moderation approach. The chain-of-responsibility pattern for safety checkers was suggested by AI and validated by me.

2. **Code scaffolding** — Django project structure, model definitions, serializer/view boilerplate, and test scaffolding were generated with AI assistance. Each file was reviewed and modified before acceptance.

3. **Regex patterns** — The keyword safety checker regex patterns were AI-assisted. I reviewed and tested each pattern, fixing false positive/negative cases (see corrections below).

4. **Test generation** — Unit and integration test cases were generated with AI help, particularly the permission-related tests and safety checker test matrix.

5. **Documentation** — README, ARCHITECTURE.md, and this document were drafted with AI assistance.

## What AI Generated That Was Useful

- The `SafetyPipeline` aggregation pattern with `CheckResult` dataclasses
- The `send_message` orchestration flow with clear separation of input/output screening
- Category-specific canned safe responses with appropriate tone for children
- The mock adapter with keyword-based deterministic responses for testing

## Examples of AI Output That Was Unsuitable and I suggested changes:

### Example 1: Regex bugs

One example:
AI generated the manipulation pattern regex with inconsistent spacing in alternation groups:
```python
# AI generated (broken):
r"(?:don'?t tell (?:your |any(?:one|body)|the) (?:parents?|...))"
# "the" lacked a trailing space, causing "don't tell the parents" to not match

# Fixed:
r"(?:don'?t tell (?:your |any(?:one|body) |the )(?:parents?|...))"
```
The test for "don't tell your parents about this" failed, revealing the bug.

### Example 2: UUID primary keys everywhere
AI used UUID primary keys on every model (User, Conversation, Message, ModerationResult). While UUIDs prevent ID guessing, they hurt index performance — UUIDs are 128 bits, random, and make joins slower. The permission layer already prevents unauthorized access, making UUIDs redundant as a security measure. For the Message table specifically, messages are always accessed through their parent conversation, so ID guessability is irrelevant. I replaced all UUIDs with standard auto-increment integer PKs which is simpler, faster, appropriate for a prototype.

### Example 3: Free-form JSON for flag categories
AI stored `flag_categories` as a free-form JSONField (list of strings). This means any arbitrary string could be stored — a typo like `"selfharm"` instead of `"self_harm"` would silently pass. I replaced this with a `FlagCategory` model (constrained table) and a ManyToMany relationship on `ModerationResult`, so categories are enforced at the database level.

### Example 4: Message role stored as text
AI used `CharField` with `TextChoices` for the message role field, storing full strings like `"assistant"` (9 bytes) per row. In a table that grows with every message, this is wasteful and as table grows to millions of messages it is just redundant repeated information. I changed it to `SmallIntegerField` with `IntegerChoices` (0=user, 1=assistant, 2=system) which is 2 bytes per row.

### Example 5: No logging in the message flow
AI did not add any application-level logging to the core `send_message` orchestration. The only logs were Django's default HTTP request lines (method, path, status code) — nothing about which adapter was called, whether input/output was flagged, token usage, or which checkers ran. I added structured `logger.info()` calls at each step of the flow so the full pipeline is visible in `docker compose logs -f backend`: message received, input screening result, adapter call with model/token info, output screening result, and flagged/fallback decisions. This still is not production level but better than no logging.

### Example 6: User message disappears while waiting for AI (UI level bug)
The AI-generated frontend cleared the input field and waited for the full API response before showing anything. The user's message visually disappeared for 1-3 seconds during the AI call, making it look broken. I added optimistic rendering — the user's message appears immediately as a temporary bubble, then gets replaced with the real server response (including moderation data) when the API returns. On error, the temp message is removed.

### Example 7: System prompt as a static inline string
AI generated the system prompt as a single hardcoded string constant (`SYSTEM_PROMPT = """..."""`) with no structure. The assignment explicitly requires "construct prompts intentionally" — a static blob doesn't demonstrate intentional construction. I restructured it into named parts (`PERSONA`, `SAFETY_RULES`, `BEHAVIORAL_GUIDELINES`) assembled by a `build_system_prompt()` function that also injects the learner's name from their user profile. This makes the prompt maintainable (change safety rules without touching persona), testable (each part tested independently).

### Example 8: Hardcoded canned responses and regex patterns
AI hardcoded both the canned safe responses (returned to learners when content is flagged) and the keyword regex patterns directly in Python source code — `SAFE_RESPONSES` dict in `services.py` and compiled regex constants in `keyword_checker.py`. Changing a canned response wording or adding a new regex pattern would require a code deployment. I moved both into the `FlagCategory` database table.

### Example 10: Over-engineering token truncation
AI initially proposed building a full token truncation system with approximate token counting (`chars / 4` heuristic) and a sliding window. For a prototype where no conversation will realistically hit token limits during demo or review, this was unnecessary complexity. I cut it and documented it as a production improvement instead.

## Example of Explicitly Rejected AI Suggestion

**Rejected: Server-Sent Events (SSE) for message delivery**

During architecture planning, the AI suggested implementing SSE for streaming AI responses. After careful analysis, I rejected this because:
1. It would require async Django views, adding significant complexity
2. Output safety screening creates a design tension with streaming and it is not much helpful anyway since ai response also goes through our safety pipeline.

I documented SSE as a production improvement in ARCHITECTURE.md and TRADEOFFS.md instead.
