# LegalAI vendor research pattern

Session signal: the user explicitly reinforced: do not invent anything; if something is unclear, ask or mark it as unknown. For vendor/legaltech research this must be embedded in the workflow, not treated as a generic style preference.

## Useful decomposition

For large LegalAI / vendor landscape research, split into parts:

1. Scope and market map.
2. Vendor landscape by class, not one giant file:
   - universal legal AI assistants;
   - contract review / drafting;
   - CLM / agreement management;
   - DMS / eDiscovery / knowledge layer.
3. Jurisdiction and regulatory barriers.
4. Requirements and scoring matrix.
5. Recommendations and pilot plan.

This reduces hallucination risk and makes it easier to verify sources.

## Evidence template per vendor

Use the same structure for each vendor:

- what this platform is;
- confirmed scenarios / target users;
- confirmed document capabilities;
- applicability to the target legal domain or jurisdiction;
- security / privacy claims;
- deployment / data residency;
- pricing;
- limitations;
- RFI questions;
- source URLs.

## Required wording for unknowns

Use explicit labels:

- "publicly not disclosed";
- "not confirmed in the sources found";
- "requires RFI";
- "hypothesis to validate with the vendor";
- "vendor-stated metric, not independently verified here".

Do not replace these with confident prose.

## RFI questions that usually matter for LegalAI

- Does the platform support the target legal system, e.g. English law, with specific sources/content modules?
- What documents can be uploaded, and what are the limits?
- Where are uploaded documents, prompts, outputs, logs and embeddings stored?
- Are customer documents used for training, fine-tuning, evaluation, support review, or model improvement?
- What is the retention period and deletion mechanism?
- Which sub-processors and model providers are involved?
- What data residency regions are available?
- Is on-prem, private cloud, or sovereign deployment available?
- What security certifications apply, and to which product scope?
- How is legal professional privilege / attorney-client confidentiality protected?
- Are citations grounded in authoritative legal sources and auditable?
- Are audit logs, admin controls, export logs and matter-level permissions available?

## Handling partial or blocked sources

If an official vendor page is blocked, dynamic, returns 403/404 after a site migration, or cannot be extracted cleanly:

- prefer another official page on the same domain first;
- use official search snippets only as limited evidence, not as full-page confirmation;
- explicitly write the access limitation in the research file;
- avoid upgrading snippet-level evidence into broad claims;
- add an RFI/security-pack question for anything that could not be verified;
- if a product has moved or rebranded, record the redirect/rebrand as observed, but do not assume old security/pricing pages still apply.

## Pitfalls

- Do not infer English-law suitability from generic phrases like "global legal database" or "law firms use us".
- Do not infer no-training from generic privacy language.
- Do not infer regional hosting from the existence of regional offices.
- Do not treat demo pages, review blogs, or market articles as equivalent to official vendor documentation.
- Do not treat vendor ROI/productivity claims as independently validated outcomes unless an independent study/source was actually checked.
- Do not silently omit access limitations; they are part of the evidence quality assessment.
