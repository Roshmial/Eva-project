# LegalAI platform research pattern

This reference captures the reusable pattern from a session researching AI/LegalTech platforms with UI for legal-document work, applicability to English-law documents, and deployment constraints across Russia, China, Hong Kong, Singapore, India, UAE, Indonesia, Malaysia, Pakistan, and Bangladesh.

Use it as an example for future enterprise vendor research, not as a permanent vendor ranking. Vendor facts may become stale; the durable lesson is the structure and evidence discipline.

## Effective structure used

The research worked best as several markdown files plus an index:

1. `scope_and_map` — scope, exclusions, market map, initial hypotheses.
2. `vendor landscape` split by segment:
   - universal LegalAI assistants;
   - contract review and drafting;
   - CLM / agreement management;
   - DMS, eDiscovery, and knowledge layer.
3. `jurisdiction_barriers` — regulatory, privacy, cross-border transfer, privilege/confidentiality, cloud/data residency, and local implementation constraints by jurisdiction.
4. `requirements_and_scoring` — must-have / should-have / could-have requirements, weighted scoring, scenario matrices, RFI checklist, demo checklist, pilot design, and red flags.
5. `recommendations` — scenario-based shortlist, deployment options, trade-offs, pilot plan, and next-step RFI/demo sequence.

This avoided model/tool timeouts and reduced hallucination risk compared with trying to produce one huge report.

## Evidence standard

For every vendor, keep a strict boundary between public facts and inference.

If details are not confirmed publicly, write:

- `публично не раскрыто`;
- `требуется RFI`;
- `требуется demo`;
- `требуется security pack`;
- `требуется проверка в пилоте`.

Do not infer English-law suitability from generic LegalAI marketing. Explicit UK/English-law positioning, authoritative legal content, citation/source grounding, and testing on English-law documents are stronger evidence. If not available, keep suitability as a hypothesis.

## Vendor profile template used

For each vendor, use the same structure:

- what the platform is;
- main scenario;
- work with legal documents;
- applicability to English-law documents;
- deployment, if publicly disclosed;
- security / privacy / no-training, if publicly disclosed;
- pricing, if publicly disclosed;
- limitations;
- RFI questions;
- sources.

## Important framing lessons

1. A LegalAI platform should not be selected by model strength alone.
   The buyer must evaluate legal quality, source grounding, citability, explainability, security/privacy, data use, auditability, access controls, integrations, deployment constraints, and total cost.

2. CLM is not the same as deep legal analysis.
   CLM tools are often strongest as an operating system for contract process: intake, drafting workflow, approvals, repositories, obligations, renewals, and integrations. They may still need a separate legal drafting/review assistant.

3. DMS/eDiscovery/knowledge tools should be evaluated through governance.
   For these tools, the key questions are access controls, matter permissions, audit trail, privilege handling, document lifecycle, and secure AI over internal content. AI over weak document governance can increase risk.

4. Recommendations should be by workflow, not by universal winner.
   Separate shortlists for legal research/drafting, English-law contract review, CLM, due diligence, litigation/eDiscovery, and internal knowledge search.

## Scoring pattern

A baseline 100-point matrix can include:

- legal workflow fit — 15;
- English-law/domain capability — 10;
- output quality — 15;
- source grounding and citations — 10;
- security and privacy — 15;
- data residency and cross-border controls — 10;
- governance and auditability — 10;
- integrations and architecture fit — 5;
- implementation and adoption — 5;
- commercial model — 5.

Adjust weights by scenario. For example, eDiscovery should put more weight on auditability and defensibility; contract review should put more weight on clause quality, playbooks, redlining, and English-law fit.

## Red flags captured

Hard red flags:

- no contractual no-training commitment;
- hosting regions and data flows not disclosed;
- no DPA or sub-processor list;
- AI does not respect matter/document permissions;
- no audit logs;
- no reliable deletion/export/exit path;
- vendor refuses customer-document pilot;
- output cannot be traced to sources;
- security review cannot be completed.

English-law red flags:

- platform gives US-style clauses in English-law contracts;
- platform mixes UK, US, EU, and generic common-law assumptions;
- platform cannot explain governing law and jurisdiction clauses;
- platform mishandles indemnity, liability, warranties, termination, and dispute-resolution concepts across jurisdictions.

## Writing style for Misha

Use Russian. Prefer a reader-friendly narrative with explanatory transitions. Bullets are fine for lists, checklists, and matrices, but introduce each section with why it matters and how to use it. Avoid dry vendor-card dumps unless the user explicitly asks for a compact table.

For final Russian reports, do an editorial language pass rather than only mechanical substitutions. In this session, a broad auto-normalization approach risked damaging filenames, URLs, citations, and product names, so the better reusable pattern was to produce a clean reader-facing final report in Russian and then search for accidental English business words. Keep English only where it is justified: product/company names, accepted abbreviations, legal document abbreviations, and stable domain terms such as LegalAI, CLM, DMS, eDiscovery, SaaS, API, LLM, RFI, NDA, MSA, DPA, UK / English law.