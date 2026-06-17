# Reclassification notes for "требует уточнения" posts

Session outcome: a manual pass over the current 7-day window showed that many ambiguous posts can be reassigned without adding new categories, but only if the main semantic center is respected and the agent avoids stretching the label.

## Durable workflow note

The analytics artifact `analytics/telegram_digest_analytics_last7d_current.json` exposes `requires_review_posts`, but in the observed build it contains only a capped subset (20 items), not the full residue. When the user asks to reclassify all ambiguous posts in the current 7-day window, do not rely on that list alone.

Preferred recovery path:
1. Enumerate the relevant `raw_logs/*_summary_input.json` files for the date window.
2. Re-run `build_digest_payload(...)` over each summary file.
3. Collect every row where `тип поста == "требует уточнения"`.
4. Only then do the semantic reassignment pass.

This is a workflow lesson, not a product limitation claim: use the analytics file as a convenience view, not as the authoritative full queue.

## Reclassification patterns that proved stable

### Move to `корпоративная новость`
Use when the post is primarily about:
- internal/company status updates;
- appointments, dismissals, bankruptcy, deaths, management reshuffles;
- awards/rankings/status recognition;
- greetings/holiday posts;
- broad company-result news when the message is about the company event, not market analysis.

Examples from the pass:
- Kept run-club / employee activity posts;
- Lanit family/kids tournament posts;
- TAdviser posts about layoffs, bankruptcy, executive appointments, death notices;
- ranking/status announcements like Borlas/BeringPro market positions.

### Move to `обзор рынка`
Use when the post is mainly a market-facing industry or regulatory update and none of the more specific buckets dominate.
This was the least-bad existing bucket for:
- standards and regulator rules;
- sector trend pieces;
- article-style market summaries;
- broad infrastructure/security/industry developments without a formal research artifact.

Examples from the pass:
- TAdviser posts about cybersecurity rules for Gosooblako operators;
- FSTEC maturity assessment plans;
- digital-ruble protection standard;
- optical storage usage by regions;
- WealthTech market-development articles.

### Move to `аналитика`
Use when the post explains implications, barriers, economics, or strategic meaning, but is not centered on a formal research artifact.

Examples from the pass:
- TAdviser piece on what enterprise customers expect from system integrators;
- Kept commentary on the economics of power-transfer fees for data centers;
- Reksoft post on the Indonesian IT market as an export direction.

### Move to `кейс`
Use when the post states actual implementation, migration, pilot, automation, or measurable effect — even if the current classifier hesitates.

Examples from the pass:
- NORBIT / RNPK metadata-governance implementation;
- Lanit / Onlanta AI secretary pilot with explicit two-month results;
- TAdviser pieces with deployed AI impact or completed migration/modernization outcomes.

### Move to `мероприятие`
Use when the real center is the event, webinar, session, conference, contest, or podcast episode — even if the text includes useful content or expert opinions.

Examples from the pass:
- Kept webinar invitation about 1C budgeting projects;
- Moscow Exchange annual reporting competition announcement;
- NORBIT + Goodt webinar;
- DRT M&A event;
- B1 / PMEF session recap when the core frame is the speaker appearing at the session.

### Move to `партнерство`
Use when the post is about a signed agreement, alliance, strategic collaboration, ownership stake, or named cross-company cooperation.

Examples from the pass:
- Lanit × Yandex B2B Tech;
- B1 agreement with Lipetsk region;
- Softline / VPG Lazervan agreement;
- Astra buying 26% of AiB.

### Move to `интервью/комментарий`
Use when the post centers on a person publicly commenting, discussing, or appearing in an interview/podcast/media slot.

Examples from the pass:
- TAdviser post where a CIO talks about AI-agent adoption in banks;
- B1 / Vedomosti comment-style post on buyer rationality;
- Yakov & Partners podcast episode.

### Move to `реклама услуг`
Use when the commercial CTA is the core of the post, not an incidental tail.

Examples from the pass:
- B1 monthly legislative digest + subscription consulting support offer.

## Important caution

Do not add a new category just because the existing dictionary feels slightly narrow. First choose the closest semantic center among the agreed buckets. Only propose a new type if a substantial residue remains after a careful pass and several posts still cannot be placed without obvious distortion.