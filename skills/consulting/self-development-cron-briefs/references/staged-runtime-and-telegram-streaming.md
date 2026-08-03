# Staged runtime refactor for daily briefs and Telegram streaming disable

Use this reference when a recurring Telegram daily brief keeps regressing even after multiple prompt-level fixes.

## When this pattern applies

Signals:
- the same class of wording defect keeps returning after several spec edits;
- anti-repeat, style bans, and self-check instructions are already present, but bad outputs still leak;
- the user explicitly says the problem is no longer one more wording fix, but the pipeline itself;
- Telegram streamed delivery is noisy or flaky and edits/flood-control start polluting the UX.

## Practical diagnosis

A giant single daily spec usually fails in one of three ways:
1. generator and critic are fused, so the model both writes and approves its own weak text;
2. the spec becomes a mixed regulation document and starts inducing polished artificial wording by its own weight;
3. repeated quality instructions stay declarative because there is no staged control surface.

## Better contour

Split the daily runtime into separate stage files:
- `00-overview.md`
- `10-context-and-constraints.md`
- `20-generator.md`
- `30-critic.md`
- `40-fallback.md`
- `runtime-prompt-v3.md`

The cron prompt should explicitly sequence:
`context -> generator (fixed candidate count) -> critic -> fallback`

## Stage semantics

### Context / constraints
Collect:
- date/time;
- real city of the day;
- travel window constraints;
- recent real daily outputs;
- recently discussed route/place/media suggestions that must not be reintroduced as if new.

### Generator
- generate a fixed small set of candidates;
- do not self-evaluate here;
- aim for short Telegram-like prose, not editorial polish.

### Critic
- do not invent a new text from scratch if one candidate already passes;
- reject candidates that are useful but still sound artificial;
- treat duplication, artificiality, and travel unreality as hard fails.

### Fallback
- if all candidates are weak, ship a simple utilitarian daily instead of the least-bad polished one.

## Telegram delivery lesson

If Telegram streaming/edit delivery becomes unstable, disable streaming at the platform level first instead of broad global shutdown:
- `display.platforms.telegram.streaming = false`
- `gateway.platforms.telegram.streaming = false`

Leave global `streaming.enabled` unchanged unless there is a broader reason.

## Verification pattern

After the refactor, verify four facts separately:
1. the cron job prompt now points at the staged files;
2. a real manual run produced a fresh output artifact;
3. delivery to Telegram succeeded;
4. post-change gateway logs no longer show fresh streaming-specific failures such as edit-not-found / flood-control / suppress-normal-final-send for the new run window.

## Why this matters

This is not just prompt cleanup. It changes the control model:
- generator no longer carries all quality logic;
- critic becomes a real reject stage;
- fallback prevents sending the most polished bad answer;
- Telegram reliability is improved without disabling streaming globally for other platforms.
