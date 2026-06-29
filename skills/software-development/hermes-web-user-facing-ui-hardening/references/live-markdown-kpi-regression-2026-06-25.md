# Live markdown regression: KPI chat at Victoria user (2026-06-25)

## When this reference matters

Use for Hermes Web user-facing markdown regressions where the user says a mixed response was rendered as one giant table or that a fix "still didn't work" in the live UI.

## Concrete reproduction shape

Live user: `vdoroninav@gmail.com`
Live thread: `KPI`
Relevant assistant messages observed through live API:
- `901`
- `903`

Both messages were mixed-content markdown, not table-only answers.

### Message 901 structure (live content)
- intro paragraph
- numbered/bulleted metric tree
- horizontal rule `---`
- bold section title
- markdown table
- more text/list after the table

The first real table starts only at line 41.

### Message 903 structure (live content)
- plain intro note
- direct-answer paragraph
- horizontal rule `---`
- heading `### 1. ...`
- markdown table
- more paragraphs
- another `---`
- another heading
- second markdown table
- lists and closing text

The first real table starts only at line 10.

## Durable lesson

If the user reports that the whole assistant answer is visually "inside a table", do not assume the table-start detector is wrong. First verify the parser's block structure on the real message text.

For this session, a manual regex parser kept producing iterative false fixes. The robust path was:
1. pull the exact live message text;
2. inspect where a table should start;
3. inspect the parser's produced block sequence;
4. if the message is mixed-content (`paragraph + hr + heading + table + list`), replace brittle custom block parsing with token-based markdown parsing.

## Practical verification pattern

1. Fetch the exact live message from the real runtime/API, not from a stale local DB.
2. Check line numbers for the first valid markdown table header + separator pair.
3. Run the current markdown parser on that exact text and record the block sequence.
4. If the sequence is already correct but the user still sees the bug, verify live frontend delivery:
   - fetch `/`
   - note the current `/assets/index-*.js`
   - compare with the locally built bundle/hash
   - only then decide whether the problem is parser logic or stale live bundle.

## Session outcome captured for reuse

A token-based parser (`marked` lexer in the existing local React frontend) produced the correct structure for the live `901` and `903` messages, including separate `paragraph`, `hr`, `heading`, `table`, and `list` blocks.

That makes this a reusable decision rule:
- for Hermes Web mixed markdown regressions, prefer real-message tokenization over continued regex patching once 2+ regex fixes have already missed the live symptom.
