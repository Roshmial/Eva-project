# Google Gemma model discovery for Hermes

Use this reference when switching Hermes to Google AI Studio / Gemini API and the target model may be Gemini or Gemma.

## Minimal checklist

1. Put the key in `~/.hermes/.env` as `GOOGLE_API_KEY` or `GEMINI_API_KEY`.
2. Set:
   - `model.provider = gemini`
   - `model.base_url = https://generativelanguage.googleapis.com/v1beta`
3. Query the live models list before choosing the model slug.
4. Pick the exact model name returned by Google.
5. Verify with `hermes chat -q`.

## Why discovery matters

The family name and the exact callable slug may differ.

Example of a wrong assumption:
- guessed: `gemma-4-31b`

Live API result in this session:
- `models/gemma-4-31b-it`
- `models/gemma-4-26b-a4b-it`

So the correct Hermes model value was:
- `gemma-4-31b-it`

## Practical implication

If Hermes returns a Google 404 like:
- `model ... is not found for API version v1beta`

first suspect a wrong model slug, not a broken provider setup.

## Verification pattern

After configuration, run a tiny prompt through Hermes itself rather than only testing raw curl.

Reason:
- raw API success proves key + endpoint;
- Hermes success proves provider wiring, adapter behavior, and model slug are all correct.
