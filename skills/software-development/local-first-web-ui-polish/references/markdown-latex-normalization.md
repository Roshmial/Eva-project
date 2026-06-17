# Markdown normalization for LaTeX math symbols in Hermes Web React

The Hermes Web React frontend includes a `normalizeMarkdownText()` function in `App.jsx` that preprocesses markdown content before rendering. It converts LaTeX math symbols to Unicode characters for safe client-side rendering without MathJax/KaTeX.

## Function location

`services/frontend-react/src/App.jsx` → `normalizeMarkdownText(text)`

## Supported patterns

| LaTeX input | Unicode output |
|-------------|----------------|
| `$\to$` / `$\\to$` | `→` |
| `$\rightarrow$` / `$\\rightarrow$` | `→` |
| `$\times N$` / `$\\times N$` | `×N` |
| `$\uparrow$` / `$\\uparrow$` | `↑` |
| `$\downarrow$` / `$\\downarrow$` | `↓` |
| `$\leftarrow$` / `$\\leftarrow$` | `←` |
| `$\leftrightarrow$` / `$\\leftrightarrow$` | `↔` |

Both single-backslash (`$\to$`) and double-backslash (`$\\to$`) forms are handled (the latter appears when LaTeX is escaped in JSON strings).

## Implementation pattern

```javascript
function normalizeMarkdownText(text) {
  return String(text || '')
    .replace(/\$\\to\$/g, '→')
    .replace(/\$\\\\to\$/g, '→')
    .replace(/\$\\rightarrow\$/g, '→')
    .replace(/\$\\\\rightarrow\$/g, '→')
    .replace(/\$\\times\s*([^$]+)\$/g, '×$1')
    .replace(/\$\\\\times\s*([^$]+)\$/g, '×$1')
    .replace(/\$\\uparrow\$/g, '↑')
    .replace(/\$\\\\uparrow\$/g, '↑')
    .replace(/\$\\downarrow\$/g, '↓')
    .replace(/\$\\\\downarrow\$/g, '↓')
    .replace(/\$\\leftarrow\$/g, '←')
    .replace(/\$\\\\leftarrow\$/g, '←')
    .replace(/\$\\leftrightarrow\$/g, '↔')
    .replace(/\$\\\\leftrightarrow\$/g, '↔');
}
```

## Usage

The function is called at the start of `renderMarkdownContent()`, `renderMarkdownParagraph()`, and `renderMarkdownTable()` so all markdown paths benefit from the normalization.

## Adding new symbols

To add a new LaTeX symbol:
1. Add two `.replace()` lines: one for single-backslash, one for double-backslash
2. Use the Unicode character directly in the replacement
3. Rebuild: `npm run react:build`
4. Restart the frontend unit

## Why not MathJax/KaTeX

This is a local-first, zero-dependency chat UI. Full LaTeX rendering would add significant bundle size and runtime complexity. The normalization approach covers the most common arrow/multiplication symbols used in technical chat responses while keeping the renderer simple and dependency-free.