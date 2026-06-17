# Russian marketplace access notes

Captured from live tender-source triage on 2026-06-01. These are source-specific patterns to verify again in future sessions, not universal claims about the platforms forever.

## B2B-Center

Observed practical status: usable from the current environment.

What worked:
- public search/listing paths under `/market/`;
- public tender cards, including old and new card layouts;
- extraction of buyer/organizer, subject, publish date, deadline, and source URL from public pages.

Observed limitations:
- site root could answer with `403 Forbidden` while list/card pages still worked;
- many newer public cards did not expose price publicly;
- some extra blocks were visible only to registered users.

Practical takeaway:
- do not reject the source just because the homepage returns 403;
- validate actual list/card URLs first;
- treat missing public price as a field-level limitation, not a full source failure.

## Fabrikant

Observed practical status: partially accessible from the current environment.

What worked:
- public search page opened;
- page/client bundle exposed query parameter names such as `date_publication_from`, `date_publication_to`, `sort_order`, `sort_direction`, `page_limit`, `page_number`;
- export endpoint pattern was identifiable as `/procedure/search/api/xls?...`.

Observed blocker:
- export endpoint returned `401 Unauthorized` in live testing;
- public HTML response exposed only incomplete embedded trade data, insufficient for a clean verified same-day result set without deeper client-side execution/auth.

Practical takeaway:
- classify as partial access, not full success;
- separate “search page reachable” from “reliable public extraction available”.

## Bidzaar

Observed practical status: blocked by anti-bot in the current environment.

Observed blocker:
- redirect to captcha / Yandex anti-bot challenge;
- no practical public card retrieval without manual challenge completion.

Practical takeaway:
- mark as `не собрано: anti-bot` for unattended collection.

## Roseltorg

Observed practical status: blocked by network reachability from the current environment.

Observed blocker:
- DNS resolution worked;
- TCP connection to 80/443 timed out before useful HTTP exchange.

Practical takeaway:
- classify as `не собрано: network`;
- do not over-interpret as a permanent platform issue — it is an environment/path accessibility result.

## Reporting pattern that worked well

For user-facing delivery, split output into:
1. final clean CSV with only usable public rows;
2. separate short status summary for excluded/problematic sources.

When asked to “убирай и подбивай”, remove diagnostic rows from the final CSV and report:
- total usable rows;
- rows by source;
- count with known public price;
- count without public price;
- sum only across confirmed public prices.
