# Focus vs recommendation and poisoned examples

Session lesson: tuning daily digests by repeatedly patching a cron prompt can fail even when many bans are present, if the prompt still contains bad example lines framed as "good".

## Durable lessons

### 1. Bad examples inside the prompt are stronger than abstract bans
If the prompt says something like "good level" and includes lines such as:
- `собрать внятный рабочий день и к вечеру выдохнуть`
- `закрыть главное по работе`
- `довести до конца один важный рабочий кусок`

then the model tends to reuse exactly those safe, empty formulas in production, even when nearby rules ban generic wording.

Rule: remove weak examples entirely instead of hoping that surrounding constraints will overpower them.

### 2. A positive focus can still be bad
The user corrected that a focus line should be a goal, not a prohibition, but that was not enough.

These still failed in practice because they are portable, vague, or soft-therapeutic:
- `собрать внятный рабочий день`
- `выдохнуть к вечеру`
- `закрыть главное на сегодня`
- `довести до конца один важный рабочий кусок до вечера`
- `пройти день ровно`

Rule: reject any focus that could be pasted into most weekdays without noticeable loss of meaning.

### 3. Focus and recommendations must be different layers
A common failure pattern:
- focus: generic work-completion line
- recommendation 1: ticket/booking/train check
- recommendation 2: another softer line about the same trip or same work storyline

This reads like one idea repeated three times.

Rule: if recommendation 1 already uses the trip/admin storyline, recommendation 2 must switch layer entirely: music, video, walk, event, calmer evening, or another genuinely different support move.

### 4. Multimedia is optional
Forcing a media recommendation every day often creates random filler.

Rule: when the media suggestion does not clearly help the day, omit it. A clean short digest without media is better than an artificial playlist/video insert.

### 5. Test discipline for daily tuning
Do not declare success from one improved run.

Use this loop:
1. patch spec/skill/prompt;
2. run the cron job manually;
3. inspect the actual latest delivered text;
4. score the result against the user's explicit complaints;
5. repeat until quality is stable rather than lucky.

A single decent run is not proof of a 9/10 system.