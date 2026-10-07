# Product case study: Ross Recruit Alerts

## Context and hypothesis

This project addresses an MBA candidate’s recurring recruiting task: monitor new opportunities and decide which deserve attention. The implementation targets Ross Recruit, with filters for events and job postings and a watch list for registration openings.

The hypothesis is that proactive, relevant alerts reduce repeated portal checks and shorten the time between an opportunity becoming available and a candidate noticing it. This is a hypothesis to validate, not a measured outcome.

## User journey

1. The candidate chooses sources, relevance filters and events to watch.
2. They complete portal login and MFA; the resulting session supports subsequent queries.
3. A first poll establishes a baseline of existing items.
4. Later polls identify previously unseen, eligible items and watched registration openings.
5. A notification provides context and a link back to the portal, where the candidate decides what to do.
6. If authentication expires, the administrator receives a recovery notice and renews the session locally.

## Prioritization

| Scope | Rationale | Status |
| --- | --- | --- |
| Event and job-posting detection | Core monitoring job | Implemented |
| Relevance filters | Avoid broad, noisy alerts | Implemented; tailored to one context |
| Baseline and observed-ID state | Avoid repeat notifications for the same item | Implemented; delivery failures remain a gap |
| Registration-open watch | Alert when an existing opportunity becomes actionable | Implemented |
| Session recovery | Keep interruption understandable and recoverable | Implemented; human login required |
| Per-user preferences and onboarding | Support users with different recruiting goals | Proposed |
| Reliable delivery and retries | Reduce missed alerts after transient failures | Proposed |
| Analytics or outcome measurement | Test value and guide iteration | Proposed; no instrumentation claims |

## PM skills demonstrated

| Skill | Evidence in this project |
| --- | --- |
| Problem framing | Defined a recurring monitoring job and an attention-cost hypothesis |
| MVP prioritization | Focused on detecting opportunities and notifying, with portal links for action |
| Product judgment | Balanced relevance, coverage, polling cost and notification fatigue |
| Technical fluency | Integrated authenticated queries, browser sessions, state, SMTP and scheduled execution |
| Lifecycle thinking | Included baseline behavior, expiry notices and renewal tools |
| Metrics design | Defined a validation plan below; metrics are not yet measured |

These are attributes of the artifact. They do not imply a team leadership role, formal user study or business impact that the repository cannot substantiate.

## Proposed validation and metrics

Start with a small opt-in pilot. Observe participants’ current monitoring habits, then compare their experience using alerts over a defined period. Ask which alerts were useful, which opportunities were missed and whether notifications became distracting.

| Question | Proposed measure | Guardrail |
| --- | --- | --- |
| Do useful opportunities get noticed sooner? | Median and 95th-percentile time from source availability to delivered alert, using source timestamps when available | Separate scheduler delay from retrieval and delivery delay |
| Are alerts relevant? | Participant-rated useful alerts divided by reviewed alerts | Report sample size and missed-opportunity feedback |
| Does the service reduce checking effort? | Self-reported portal checks before and during the pilot | Do not treat self-report as observed behavior |
| Does delivery work consistently? | Successful delivery attempts divided by attempted notifications | SMTP acceptance is not proof of inbox delivery or reading |
| Is recovery manageable? | Time from detected session expiry to a verified successful poll | Track recurring expiry and renewal failures |

Interview invitations and job offers are downstream outcomes with many causes; this tool alone should not be credited for them.

## Next iteration

Prioritize reliability before adding channels or a dashboard. Persist pending notifications separately from delivered notifications, make commit failures visible and exercise failure paths with synthetic fixtures. Then make filters easier to configure and validate their relevance with users. Broaden source coverage only after checking which opportunities the current scan misses.

The service does not provide exactly-once delivery. First-run behavior, concurrent execution, scheduler delays, notification failures and state persistence need explicit integration tests before expansion.
