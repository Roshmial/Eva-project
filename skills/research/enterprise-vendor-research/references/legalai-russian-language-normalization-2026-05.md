# LegalAI reports: Russian-language normalization pattern (2026-05)

Use this reference when editing Russian LegalAI / LegalTech research for Misha after drafting, merging, or rewriting a large report.

## User correction that triggered this pattern

Misha asked to remove unnecessary Anglicisms from the LegalAI report. The issue was not English product names or standard abbreviations, but mixed Russian-English business prose that made the report feel less natural and less reader-friendly.

## What to preserve in English

Preserve English where translation would reduce precision or distort industry meaning:

- company and product names: LegalOn, Spellbook, Robin AI, Lexis+ AI, Harvey, Legora, vLex Vincent AI, Kira, Luminance, Ironclad, Juro, Sirion, ContractPodAi, Docusign IAM, Workday/Evisort, LinkSquares, iManage, NetDocuments, Litera, Relativity, Everlaw, DISCO;
- accepted abbreviations: LegalAI, AI, CLM, DMS, RFI, LLM, GDPR, SOC, ISO, SaaS, SSO/SAML;
- fixed domain terms when they are clearer than forced Russian: eDiscovery, redlining, due diligence, SOC 2, ISO 27001.

## Replace unnecessary Anglicisms in Russian prose

Common replacements:

- vendor -> поставщик;
- workflow -> процесс / рабочий сценарий;
- deployment -> развёртывание / вариант развёртывания;
- security -> информационная безопасность;
- privacy -> конфиденциальность / защита данных;
- knowledge layer -> слой юридических знаний;
- governance -> управление / контроль;
- pricing -> цена / модель ценообразования;
- scoring -> оценочная матрица / оценивание;
- shortlist -> шорт-лист / сценарный список;
- pilot -> пилот / пилотный проект;
- demo -> демонстрация;
- review -> проверка / анализ, depending on context;
- drafting -> подготовка документов / подготовка правок;
- red flags -> красные флаги / признаки исключения;
- templates -> шаблоны;
- penetration testing -> тесты на проникновение;
- whitepaper -> документ / технический документ.

## Editing workflow

1. Make targeted replacements, but avoid blind global substitutions across URLs, filenames, citations, product names, and official titles.
2. Run a residual Latin-token scan and inspect anything that is not a product name, accepted abbreviation, URL, or citation.
3. Read representative sections manually after replacements. Mechanical edits often break Russian case agreement.
4. Fix grammar, not only vocabulary. The goal is natural Russian management prose, not a mechanically translated text.
5. Preserve evidence boundaries: do not make conclusions stronger while polishing wording.

## Grammar artefacts to check after replacement

Look for broken phrases such as:

- `как строить демонстрация` -> `как проводить демонстрацию`;
- `единый хранилище` -> `единое хранилище`;
- `черновик юридическая записка` -> `черновик юридической записки`;
- `проверка договоров решений` -> `решений для проверки договоров`;
- `поддержка английское право` -> `поддержка английского права`;
- `с критерии` -> `с критериями`;
- `зрелости управление документами` -> `зрелости управления документами`.

## Final quality bar

The final LegalAI report should read as Russian analytical prose with necessary technical terms, not as English vendor research translated word-by-word. Keep the structure, conclusions, uncertainty markers, RFI/demo/pilot discipline, and vendor evidence boundaries intact.