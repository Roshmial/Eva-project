---
name: enterprise-vendor-research
description: Build grounded, reader-friendly enterprise vendor/platform research reports with evidence standards, segmented vendor landscape, RFI/demo checklists, scoring matrices, and deployment/regulatory risk analysis.
---

# Enterprise vendor research

Use this skill when the user asks for research, comparison, shortlist, market map, vendor landscape, platform selection, RFI preparation, pilot design, or scoring framework for enterprise software or professional-services technology.

This is especially relevant when the task involves LegalTech, AI tools, security/privacy requirements, multi-jurisdiction deployment, regulated data, vendor claims, or unclear public pricing/deployment details.

## Core principle

Do not turn vendor research into a list of marketing claims. First identify the actual decision frame.

There are two common frames:

1. Buyer-side selection: the user wants to choose, reject, pilot, or implement an enterprise platform.
2. Market-entry / product strategy: the user wants to launch a solution and understand market demand, competitors, barriers, required capabilities, and product niches.

For buyer-side selection, treat the report as a decision-support document for buying or rejecting a platform.

For market-entry / product strategy, do **not** structure the output as "which vendor should we buy". Treat vendors as a competitive map, requirements as market requirements for a new product, and regulatory/security constraints as product architecture requirements and barriers to entry.

Separate clearly:

- facts: confirmed by public sources or user-provided material;
- interpretations: your reasoned conclusions based on those facts;
- hypotheses: plausible but not confirmed, requiring RFI, demo, pilot, or security review.

If pricing, deployment, hosting region, data use, no-training commitment, certifications, customer-managed keys, security controls, or jurisdiction-specific suitability are not public, say so explicitly: `публично не раскрыто`, `требуется RFI`, `требуется demo`, or `требуется security pack`.

## Recommended workflow

1. Define scope and decision question.
   - What workflow is being improved?
   - Who will use the platform?
   - What documents/data are in scope?
   - Which jurisdictions, languages, legal regimes, or internal policies matter?
   - What is explicitly out of scope?

2. Split the market into meaningful segments.
   Avoid comparing unlike tools as if they solve the same problem. For example, for LegalAI split into universal legal assistants, contract review/drafting, CLM, DMS/knowledge layer, and eDiscovery/litigation review.

3. Build vendor profiles with a consistent structure.
   Use a repeatable structure so the user can compare vendors without re-learning the format each time:
   - what the platform is;
   - main scenario/use case;
   - document workflow fit;
   - domain or jurisdiction fit;
   - deployment/hosting if public;
   - security/privacy/no-training if public;
   - pricing if public;
   - limitations;
   - RFI questions;
   - sources.

4. Preserve evidence boundaries.
   Never infer that a vendor is suitable for a specific jurisdiction, document type, or regulated use case just because it markets itself as AI, legal-grade, enterprise-grade, or global. Treat unsupported suitability as a hypothesis to test.

5. Add regulatory and implementation barriers separately from vendor marketing.
   Cover privacy, cross-border transfer, data residency, privilege/confidentiality, cloud acceptance, auditability, access control, procurement, and local adoption constraints.

6. Create a requirements and scoring layer before recommendations.
   Include business, functional, quality, non-functional, security, integration, jurisdictional, and commercial criteria. Mark hard gates separately from weighted criteria.

7. Finish with scenario-based recommendations, not a single universal winner.
   Recommend shortlists by use case and risk posture: conservative, balanced, aggressive, or similar scenarios. Explain trade-offs and what must be tested in RFI/demo/pilot.

## Reader-friendly writing standard

For Misha, research documents should not be a dry bullet dump. Use explanatory paragraphs that tell the reader how to interpret the section and why it matters for the decision. Bullets are acceptable for checklists, matrices, vendor facts, and RFI questions, but major sections should include connective explanation.

For Russian-language research, keep the main prose in Russian. English terms are fine when they are normal domain terms (for example RFI, demo, pilot, shortlist, scoring, CLM, DMS, eDiscovery, data residency, audit trail), but avoid unnecessary English connective words or sentence scaffolding such as `and`, `or`, or `rather than` inside otherwise Russian prose.

For Misha, add a final language-normalization pass after drafting or merging large reports. Search for accidental English business words that slipped into Russian prose and replace them with natural Russian equivalents where meaning is not lost: `workflow` -> `процесс` / `сценарий`, `vendor` -> `поставщик`, `market entry` -> `выход на рынок`, `wedge` -> `точка входа`, `contract review` -> `проверка договоров`, `drafting` -> `подготовка документов` / `подготовка правок`, `risk triage` -> `первичная оценка рисков`, `source grounding` -> `привязка к источникам`, `procurement` -> `закупки`, `security` -> `информационная безопасность`, `adoption` -> `принятие продукта`, `outcomes` -> `результаты`, `players` -> `игроки`, `hallucination` -> `галлюцинация модели`. Preserve English for product/company names, accepted abbreviations, legal document abbreviations, and fixed domain terms.

Do not rely on one mechanical global-replacement pass for a large merged Russian report. It can corrupt filenames, URLs, citations, product names, and grammar. If normalization becomes messy, create a clean editorial final report that preserves the research conclusions and evidence boundaries, then run targeted searches for leftover accidental English business words.

After broad replacements, perform a grammar sanity check for broken Russian case agreement caused by replacement, especially phrases like `по субобработчикам`, `варианты резидентности данных`, `юридические методики проверки`, and `общая презентация`.

Recommendations should be analytical, not just a vendor catalogue: show the decision logic, scenario fit, trade-offs, blockers, and why a vendor class matches the workflow.

When the user is exploring launching a new solution, replace buyer-side artifacts with product-strategy artifacts:

- shortlist → competitive positioning and occupied/available market spaces;
- vendor scoring → product-niche scoring;
- implementation risks → barriers to entry and architecture requirements;
- RFI/demo questions → discovery interview questions, MVP validation criteria, and buyer objections to pre-empt;
- vendor requirements → table-stakes product capabilities and differentiators.

For market-entry research, produce competitor comparison as its own visible artifact when the user needs competitive clarity. Include: origin/headquarters and visible regions, functional matrix, non-functional/enterprise-readiness matrix, overall competitive-position comparison, and threat scoring for the intended product niche. Do not bury this in prose or buyer-style recommendations.

Do not overclaim. If evidence is weak, make the uncertainty visible instead of smoothing it over.

## Dashboard-output mode

When the user asks for a client-facing dashboard or strict structured payload rather than a prose report:

- obey the requested schema exactly and return only that payload, with no wrapper text;
- keep `reply_text` short, decision-useful, and honest about evidence quality;
- if data is partial, still return a useful minimum dashboard instead of failing closed;
- use summary cards only for the strongest, most defensible signals;
- separate hard facts from directional interpretations inside the section items;
- when market-size figures come from commercial analyst firms, present them as third-party market estimates or public report claims, not as unquestioned fact.

## Evidence gathering under weak public search conditions

If ordinary search-engine scraping is blocked or noisy:

- fall back to direct collection from authoritative public pages: vendor sites, investor/news pages, major industry reports, and reputable press;
- prefer product pages, customer/traction pages, security/deployment pages, and named research reports over SEO listicles;
- if the open web yields only partial access to market-size numbers, combine a cautious market estimate with stronger adoption signals such as customer counts, public rollout claims, workflow positioning, and security/governance messaging;
- explicitly mark where evidence is from vendor self-reporting versus independent reporting.

### Practical fallback when browser SERPs are weak but terminal web access works

A repeatable fallback for client dashboards and quick market scans:

- use DuckDuckGo Lite / HTML search pages from terminal-accessible HTTP, not the rich browser SERP, when the browser snapshot hides results or bot friction makes interaction noisy;
- extract both result links and `result-snippet` text from the HTML, because snippets often expose the only openly accessible market-size sentence from analyst-report landing pages;
- treat snippet-derived market numbers as third-party public report claims surfaced by search, not as directly verified facts from the full report;
- whenever possible, pair snippet-based market-size numbers with stronger first-hand signals from accessible pages: adoption surveys, vendor/customer traction, funding announcements, or reputable press;
- in dashboard outputs, prefer wording such as `открытые оценки`, `по открытому сниппету поисковой выдачи`, or `публично доступная оценка` so the evidence boundary stays visible.

When the research question mixes incompatible market-share concepts, do not force a single faux-precise table. Keep the layers separate and label them clearly:

- money / market-size figures;
- usage-share figures from traffic/usage sources;
- segment-specific shares such as desktop-only or mobile-only;
- product rankings or scorecards, which are not market share.

If the user still needs one client-facing dashboard, assemble it as a visible multi-layer view and explicitly mark any combined top-5 share view as an `аналитическая оценка` when it is synthesized from open segment signals rather than directly published as one official table.

See also `references/legalai-open-web-dashboard-evidence.md` for a compact LegalAI pattern and `references/russia-os-market-dashboard-evidence-2026-06.md` for a Russia OS market example of splitting market size, usage share, and ranking evidence.

## When documents become large

If the research is broad, split it into multiple markdown files and maintain an index/status file. This reduces timeout risk and makes review easier.

A useful structure:

1. scope and market map;
2. vendor landscape, split by segment if needed;
3. jurisdiction/regulatory barriers;
4. requirements and scoring framework;
5. recommendations, shortlist, pilot plan, and next steps.

After creating each part:

- update the index/status file;
- verify the file exists;
- tell the user exactly what was created and what remains.

## RFI/demo/pilot discipline

Vendor demos are not proof. Treat the following as weak evidence unless tested on customer-relevant material:

- polished generic demos;
- summaries without citations or source grounding;
- vague security claims;
- customer logos without comparable use case;
- ROI claims without methodology;
- promises that something can be configured later without cost/timeline.

A good pilot should define:

- representative documents/data;
- success metrics;
- reviewers and decision owners;
- security/privacy review path;
- pass/fail criteria;
- exit and data deletion requirements.

## Pitfalls

- Do not rank vendors globally when the right answer depends on workflow.
- Do not treat CLM, DMS, AI assistant, eDiscovery, and contract review tools as interchangeable.
- Do not assume English-language support equals English-law suitability.
- Do not assume public absence of pricing/security/deployment means weakness; mark it as unknown and request evidence.
- Do not include credentials, tokens, API keys, or connection strings in research notes. Replace any secret-like value with `[REDACTED]`.

## References

- `references/legalai-platform-research.md` — condensed session-specific pattern from the LegalAI / LegalTech platform research for English-law documents and multi-jurisdiction deployment.
- `references/legalai-russian-language-normalization-2026-05.md` — Russian-language cleanup pattern for LegalAI reports: what English terms to preserve, which Anglicisms to replace, and grammar checks after automated replacements.
- `references/legalai-market-entry-product-strategy-2026-05.md` — LegalAI market-entry/product-strategy pattern: convert vendor landscape into competitive map, include country/security barriers, functional comparison, and product-niche scoring.