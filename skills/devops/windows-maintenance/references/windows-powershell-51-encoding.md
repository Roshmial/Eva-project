# Windows PowerShell 5.1 encoding gate

- Save every shipped `.ps1` as UTF-8 with BOM. Windows PowerShell 5.1 treats UTF-8 without BOM as the active ANSI code page; Cyrillic bytes can become mojibake and even parser errors inside quoted regex literals.
- Prefer ASCII-only executable regex source when practical. Represent required Cyrillic matching with .NET regex Unicode escapes such as `\u043f`, while still retaining BOM for all other text.
- Before packaging, assert every `.ps1` begins with bytes `EF BB BF`, parse every extracted script, and run the package verifier against the extracted archive.
- Make the package verifier reject `.ps1` files without BOM in addition to checking SHA-256.
- For blocked preflight actions, print the reason immediately and do not create an empty report. For read-only audits, print stage/progress messages so a long collection does not look frozen.
- When the requested UX is comprehensive processing, first bind the orchestrator to the requested outcome. For unused-software cleanup, “comprehensive” means `analyze → select → uninstall → verify` in one interface; do not reinterpret it as a broad audit/cleanup/repair/update cycle. For an explicitly requested system-wide cycle, pass a shared `ReportRoot`, `-NoArchive`, `-SuppressReportPath`, and `StatusPath` to internal modules and package the staging directory once at the end so the user receives one report rather than one archive per stage.
- Splat named script parameters with a hashtable. Array splatting of strings such as `@('-ReportRoot',$path)` binds positionally and can silently set `ReportRoot` to the literal `-ReportRoot`.
