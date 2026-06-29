# Partial egress and search fallbacks

## When this pattern appears

Use this note when a user reports that generic web collection says `не смог`, `sources not found`, or looks like `browse is broken`, but at least one outbound probe or job run from the same runtime still succeeds.

## Concrete live pattern

Observed in a Hermes Web prod contour:
- recurring/job execution worked;
- a generic chat/web-collection request could still answer in the style of `не смог`;
- outbound probes showed mixed reachability rather than total failure:
  - `news.google.com` returned `200`;
  - some target domains returned `401/403/503`;
- search/discovery and fetchability were therefore different failure domains.

## Durable lesson

Do not collapse all of this into `no external access`.

Classify separately:
1. search provider failure or challenge;
2. per-site fetch blocking (`401/403` / anti-bot / timeout);
3. post-fetch relevance being too strict and throwing away soft-match documents.

## Hardening moves that helped

1. Add search-provider redundancy after local Hermes CLI search:
   - DuckDuckGo HTML
   - Bing HTML
   - another independent HTML fallback such as Startpage

2. Retry `401/403` once with more browser-like headers:
   - more common `User-Agent`
   - `Accept-Language`
   - `Cache-Control` / `Pragma`
   - `Upgrade-Insecure-Requests`

3. Soften the final relevance gate:
   - keep strong subject-hit matches first;
   - then allow soft thematic matches with acceptable score and non-junk pages;
   - only then return `documents_irrelevant`.

## User-facing framing

Prefer:
- "Внешний доступ есть не ко всем источникам одинаково: часть сайтов открылась, часть режет automation; итог собран по доступным материалам."
- "Проблема не в полном отсутствии внешки, а в частичной доступности источников и search/fetch ограничениях."

Avoid:
- "browse не работает"
- "у сервера нет внешки"

unless broader probes show total outbound failure across multiple independent hosts.
