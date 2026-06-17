# LegalAI market-entry / product strategy research pattern

Use this reference when the LegalAI question is not buyer-side vendor selection, but launching a new LegalAI solution.

## Trigger

User framing examples:

- «я хочу выпустить на рынок решение LegalAI»
- «что хочет рынок и какие есть ограничения/конкуренты»
- «мы не подбираем, что внедрить; мы смотрим, какой продукт делать»
- market-entry, product strategy, competitive positioning, MVP, product niche, go-to-market

## Critical framing correction

Do not structure the report as: which vendor should we select and implement.

Instead structure it as: what market demand exists, which competitors already occupy which positions, what enterprise/legal/security requirements are now table stakes, what barriers block market entry, and where a new product can realistically differentiate.

Vendor landscape becomes a competitive map, not a procurement shortlist.

Requirements become market requirements for a new product, not only evaluation criteria for buying a platform.

Regulatory and security constraints become product architecture requirements and possible differentiation, not only implementation risks.

## Recommended report structure

1. Main decision question
   - What LegalAI product could be launched?
   - Which legal/document workflows have demand?
   - Which buyer segments feel the pain?
   - Which competitors already solve parts of it?
   - Which constraints must be built into the product from day one?

2. Market demand map
   - Speed: faster document reading, contract review, risk spotting, redlines.
   - Predictability: playbooks, templates, stable outputs, corporate positions.
   - Trust: source grounding, explainability, audit trail, no hallucinated legal claims.
   - Security: no client-data training, access control, data residency, deletion/export.
   - Jurisdiction fit: explicit support for English law or other target regimes, not just English-language UI.

3. Competitive map by segment
   - Universal legal AI assistants: Lexis+ AI, CoCounsel, Harvey, Legora, vLex Vincent AI.
   - Contract review / drafting: LegalOn, Spellbook, Robin AI, Luminance, Kira/Litera, Ironclad, Ontra.
   - CLM: Ironclad, Juro, Sirion, ContractPodAi, Docusign IAM, Workday/Evisort, LinkSquares.
   - DMS / knowledge layer: iManage, NetDocuments, Litera.
   - eDiscovery / litigation review: Relativity, Everlaw, DISCO.

4. Functional and non-functional competitor matrices
   In market-entry work, do not hide the competitor comparison inside narrative recommendations. Create a separate matrix artifact when the user needs to see the competitive field clearly.

   Include four views:

   A. Origin and regional footprint table:
   - solution / product group;
   - company;
   - country of origin or headquarters;
   - visible regions of market presence;
   - primary segment;
   - caveat: if regions are inferred from public presence/customer stories rather than confirmed product availability, mark `вероятно / требует проверки`.

   B. Functional matrix by capabilities, not one global vendor ranking. Useful dimensions:
   - legal Q&A;
   - legal research with sources;
   - document summary;
   - document classification;
   - contract risk review;
   - redlining;
   - playbook-based review;
   - obligations extraction;
   - approvals;
   - repository;
   - internal document search;
   - permission inheritance;
   - audit trail;
   - privilege/confidentiality review;
   - bulk document review;
   - integrations;
   - data residency control;
   - no-training guarantees.

   C. Non-functional / enterprise-readiness matrix:
   - security pack maturity;
   - no-training terms;
   - data residency clarity;
   - access control / SSO/SAML;
   - audit trail;
   - enterprise procurement readiness;
   - legal privilege/confidentiality controls;
   - English-law evidence;
   - deployment flexibility.

   D. Competitor threat scoring for the intended niche. Do not score `best vendor overall`; score `threat to our product position`. Example dimensions:
   - functional closeness to our niche;
   - brand / trust strength;
   - public security maturity;
   - English-law relevance;
   - overall threat.

   Use simple visible scales, e.g. 0–3 for capability maturity and 1–5 for competitor threat. Mark unknowns as `?` rather than inventing coverage.

5. Country/security risk map
   For market-entry reports, include a product-facing country table:
   - country;
   - key information-security/data risks;
   - risk for a LegalAI product;
   - what must be built into product and architecture.

   Important jurisdictions from this session:
   - Russia: personal data localization, cross-border transfer procedures, high risk for foreign SaaS/LLM with citizen data.
   - China: PIPL, cross-border data mechanisms, possible local deployment or local partner need, generative AI controls.
   - Hong Kong: PDPO, PCPD AI expectations, common law privilege, transfer clauses.
   - Singapore: PDPA, Transfer Limitation Obligation, MAS TRM for financial sector, outsourcing controls.
   - India: DPDP Act, RBI localization for payment data, CERT-In style logs/incident expectations.
   - UAE: mainland/DIFC/ADGM regimes, cross-border transfer, professional secrecy, banking/cloud expectations.
   - Indonesia: PDP Law, transfer safeguards, regulated sector/public electronic system expectations.
   - Malaysia: PDPA amendments, DPO, breach notification, processor obligations, transfer assessment, AI governance guidance.
   - Pakistan: developing PDP regime, Cloud First/data classification, public-sector and banking sensitivity.
   - Bangladesh: developing data/cybersecurity regime, regional/private deployment likely for sensitive clients.

6. Product niche scoring model
   Score product directions, not vendors. Example weighted criteria:
   - customer pain severity: 20%;
   - result verifiability: 15%;
   - competitive saturation: 15%;
   - trust/security barrier: 15%;
   - narrow MVP feasibility: 15%;
   - expandability: 10%;
   - monetization: 10%.

   Candidate directions:
   - English-law contract review;
   - multi-jurisdiction document intake / triage;
   - AI layer over existing DMS/CLM;
   - vertical industry solution;
   - universal legal AI assistant;
   - full CLM with AI.

7. Recommended product position
   A strong starting hypothesis from this session:
   LegalAI for initial English-law contract review and multi-jurisdiction legal document triage for international companies, with risk spotting, suggested redlines, client playbooks, data sensitivity classification, jurisdiction/security warnings, audit trail, no-training, and multiple deployment modes.

## Writing rules for Misha

- Write in Russian as a strategic product/market report, not a procurement checklist.
- Avoid unnecessary English business words in Russian prose. Preserve product names and accepted abbreviations/terms only.
- Do not overclaim vendor capabilities or country-law compliance.
- Separate facts, interpretations, hypotheses, and product recommendations.
- Do not say “buy this” or “implement this”; say “this segment is occupied”, “this is a possible niche”, “this requirement is table stakes”, “this must be validated by interviews/pilot”.

## Pitfalls

- Do not turn the competitive map back into a buyer shortlist.
- Do not treat regulatory barriers only as legal appendix; for market entry they shape architecture, packaging, sales, and credibility.
- Do not recommend building a universal legal assistant first unless there is a strong content, distribution, or jurisdictional advantage.
- Do not ignore information security: in LegalAI, no-training, data residency, auditability, access control, and deletion/export are part of the product, not back-office details.
- Do not make the MVP too broad. Prefer a narrow, testable scenario with real documents and measurable legal-quality metrics.