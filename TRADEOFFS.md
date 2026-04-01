# Tradeoffs

## Remaining Risks

1. **Keyword list coverage** — The regex-based safety checker catches known patterns but will miss creative euphemisms, slang evolution, and context-dependent harm. This is partially mitigated by the OpenAI Moderation API layer, but neither is perfect.

2. **Single-vendor moderation** — Both the AI tutor and content moderation use OpenAI. If OpenAI has a systematic blind spot, it affects both generation and screening. A determined adversary could potentially craft prompts that bypass both layers.

3. **No rate limiting** — The API has no per-user or global rate limits. A malicious user could exhaust OpenAI API credits or create thousands of conversations.

4. **JWT in localStorage** — Stored tokens are accessible via XSS. If the frontend has a cross-site scripting vulnerability, tokens could be exfiltrated.

5. **No prompt injection defense** — The system prompt has a soft instruction to not break character, but there is no enforced detection in the safety pipeline. A learner could potentially jailbreak the AI with "ignore previous instructions" style attacks.

## Intentional Shortcuts

1. **Synchronous AI calls** — Blocks the request thread for 1-3 seconds. Acceptable for single-user prototype; production needs async workers (Celery) or async Django views.

2. **No email verification** — Users can register with any email. Production would verify email ownership before granting access.

3. **No localization for canned responses** — Canned responses are stored in the database and editable via Django admin, but only in English. Production would need localized responses based on the learner's language.

4. **No conversation title auto-generation** — Titles are user-provided or blank. Could auto-generate from the first message using the AI.

5. **No pagination on messages** — Conversation detail loads all messages at once. Fine for prototype-length conversations; production needs cursor-based pagination.

6. **No audit trail** — Moderation decisions are stored in ModerationResult but there's no separate immutable audit log for compliance. DB contents can be altered by someone and would not be ideal for audits / compliances.

7. **Message role as integer** — Stores 0/1/2 instead of "user"/"assistant"/"system" for storage efficiency. Requires mapping back to strings for the OpenAI API and frontend display. The right tradeoff for a table that grows with every message.

8. **No conversation blocking after flags** — When a message is flagged, the learner gets a safe canned response but the conversation continues. The learner can keep sending messages, and subsequent messages are still screened. In production, a deliberate policy decision needs to be made: should the conversation be locked after N flags? Should the learner be temporarily blocked? Should a teacher be notified in real-time? These are product and safety policy decisions that should involve child safety experts, not just engineering judgment. We intentionally left the conversation open for the prototype and documented it as requiring a policy decision.

## Next Engineering Priorities

1. **Prompt injection defense** — Add a dedicated safety checker for jailbreak patterns ("ignore previous instructions", "you are now...", "pretend you are...") to the safety pipeline. This is the highest-risk gap currently.

2. **Rate limiting** — django-ratelimit or API gateway level. Per-user and per-IP limits.

3. **Streaming responses (SSE)** — Buffer AI output, run safety check, then stream to client. Better UX without compromising safety.

4. **Cross-vendor moderation** — Add a third safety checker using a different provider (e.g., Anthropic's content moderation, or a custom classifier) for defense-in-depth on AI output.

5. **Observability** — Structured JSON logging, request tracing, moderation metrics dashboard. Track: flag rate over time, false positive rate (via teacher feedback), AI response latency p50/p95/p99.

6. **Background processing** — Move AI calls to Celery workers. Return message ID immediately, later client receives SSE notification when response is ready.

7. **Admin tooling** — Teacher actions on flagged conversations: dismiss false positive, escalate to admin, block learner, add notes.
