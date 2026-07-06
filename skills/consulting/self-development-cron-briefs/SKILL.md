---
name: self-development-cron-briefs
description: Design and tune recurring Hermes daily/weekly self-development briefings for Misha with test-first rollout, compact Russian style, and practical structure.
---

# Purpose

Use this skill when creating, revising, testing, or enabling Hermes cron jobs that send Misha proactive self-development messages such as a daily morning brief or a weekly review.

This skill covers both content design and rollout discipline.

# When to use

Trigger this skill when the task includes any of the following:
- daily or weekly self-development reminders;
- proactive personal-effectiveness briefings;
- rewriting the tone or structure of Eva's recurring messages;
- moving a self-development cron job between test and live delivery;
- checking whether duplicate self-development messages came from schedule overlap or from manual test runs.

# Core rules

1. Default to Misha's test-period semantics, not generic local-only rollout.
   - For Misha, a "test period" normally still delivers to Telegram.
   - Test mode means limited duration, active monitoring, and prompt refinement during the run.
   - Use `deliver=local` only when the user explicitly asks for silent/local testing.
   - Do not leave test and production variants running at the same time.

2. Prefer updating the existing job over creating a duplicate.
   - First inspect whether the perceived duplicate is actually two runs of one job: a manual test plus the scheduled run.
   - Reuse the current job ID unless there is a strong reason to split responsibilities.
   - If a time-bounded test works well, prefer promoting that same job into production by extending or removing the time limit instead of reviving an older duplicate job.

3. Write in Russian, in Eva's calm working voice.
   - Natural, compact, non-theatrical language.
   - No coaching slogans, no inflated inspiration, no rigid template feel.
   - Less "why this matters" explanation, more concrete framing.

4. Morning daily briefs must begin with:
   - `Доброе утро, Миша!`

5. Daily format is practical, not essay-like.
   - Exactly 1 main goal.
   - Exactly 2 small supporting goals.
   - Main goal should usually be the highest-value result of the day.
   - Main goal must be concrete enough that by evening the result is visible, not just the intention.
   - Prefer practical patterns such as: finish one hanging message, make one booking, pay/renew/order something specific, confirm one meeting or appointment, close one small admin or household task with a clear endpoint, or push through one concrete work result.
   - Small goals should support energy, order, learning, or momentum without competing with the main goal.
   - Small goals must be concrete, explicit, naturally phrased, and feel realistically doable.
   - Each small goal must be one clear thing, not a menu, bundle, or vague category.
   - Small goals must not be reduced-size copies of the main goal.
   - Do not skip prerequisites inside a small goal: if the action assumes a list, source, or setup that may not exist yet, include that setup in the action itself.
   - Prefer formulations like "выписать 3–5 мелких хвостов и закрыть один" over artificial shortcuts like "разобрать короткий список", unless the list clearly already exists.
   - Do not let small goals drift into generic self-help wording or abstract framing.
   - On Thursday and Friday, it is useful to add one short weekend-planning note with one realistic idea, as long as it stays lightweight and does not compete with the day's main plan.
   - In scheduled cron delivery, the final rendered brief must read as complete one-way output. If the prompt contains a slot like `one short final question`, reinterpret it as a soft closing line, not as a literal question to answer now.
   - Default rule for non-interactive cron briefs: do not end with a question mark and do not ask `Ок такой план?`, `хочешь сам выбрать фокус?`, or close variants.

6. Adapt the brief to the day type.
   - Weekdays: main goal is usually work/productivity-oriented.
   - Weekends: main goal is usually self-development, clarity, reset, or recovery.

7. Use context signals when they materially improve relevance.
   - Calendar/day-of-week context.
   - Moscow weather by default.
   - If weather is poor, do not default to walks.
   - Small goals must react to both weather and weekday/weekend mode.
   - Small ideas should be intentionally diverse across days, not just technically valid.
   - Treat diversity as a requirement, not a nice-to-have: vary the type of small step itself, not only the wording.
   - Weekend small goals may widen into social, cultural, creative, language, or destination-based ideas, but still stay lightweight.
   - Workday small goals should usually support energy, order, learning, or recovery without turning into a second major agenda.
   - If suggesting a walk or outing, anchor it to a concrete nearby destination or route from the user's location instead of a generic "go outside" idea.
   - Optional Moscow leisure suggestion: at most 1 concrete option with 1 link, only when it genuinely fits the day.

8. Weekly review should be short and grounded.
   Use this compact structure:
   - Что получилось.
   - Что мешало.
   - Главный фокус следующей недели.
   - Две поддерживающие вещи.
   - Один короткий вывод от Евы.
   Keep each block to 1–2 short sentences.

# Recommended workflow

1. Confirm whether the issue is real duplication.
   - Check if there are multiple jobs or one job with both manual `run` and scheduled execution.
   - Explain the distinction clearly to the user.

2. Put the job into the correct test mode for this user.
   - Do not assume test means `deliver=local`.
   - For Misha, default test mode is still Telegram delivery with a limited run window.
   - Use `deliver=local` only for explicitly silent experiments.
   - Keep test and production separated, but do not hide outputs from the user during a test period unless asked.

3. Rewrite the prompt around fixed output constraints.
   - Daily: greeting + day context + weather-aware framing + 1 main + 2 small goals.
   - Weekly: 5 compact blocks only.
   - Explicitly ban filler lines and coaching rhetoric.

4. Test immediately.
   - Run the cron job manually.
   - Inspect the generated output, not just the config change.
   - If text still sounds templated, tighten the prompt again and rerun.

5. Only after user approval, decide whether the chosen job stays time-bounded or becomes ongoing.
   - If the test job is the right one, prefer extending that same job or removing the repeat limit instead of creating or reviving a parallel live variant.
   - Avoid enabling a second live path in parallel.

# Prompt-writing guidance

For daily briefs, explicitly instruct the cron prompt to:
- sound like a smart colleague, not a motivational channel;
- avoid filler transitions and generic aphorisms;
- keep the text compact;
- vary wording naturally across days;
- prefer practical advice over abstract framing;
- avoid presenting several competing priorities as equally important;
- suggest indoor alternatives when Moscow weather is wet/cold;
- use session_search to inspect a long enough tail of recent daily briefs before drafting a new one when repetition risk matters; for this workflow, 10 recent morning briefs is a better default than 3 when the goal is to catch recycled leisure/support ideas;
- do not stop at session_search snippets. Snippets are only discovery. Before drafting, extract the final assistant text for the last 10 real morning briefs and make a compact working list of: main-goal category, small-goal categories, concrete objects/places/media/games, and weekend idea.
- if the retrieval path only surfaced snippets or mixed prompt text, treat the anti-repeat check as incomplete and keep digging until the actual final brief texts are visible.
- treat both wording repetition and idea repetition as real failures, not cosmetic issues;
- explicitly track repeated concrete objects, not just categories: the same place, the same game, the same article/video/media item, the same weekend-destination family, or the same fallback micro-activity still counts as repetition even if the wording changes;
- treat repeating the same concrete place or the same concrete game within roughly 14 days as a hard failure unless the user explicitly asked to revisit it;
- if a concrete suggestion appeared recently, force a different category instead of paraphrasing the same idea again;
- for known sticky fallback ideas, it is acceptable to name them explicitly in the prompt as temporary bans until the rotation stabilizes;
- do not repeat the same main-goal category on adjacent days;
- if yesterday or the day before used "навести порядок в делах", "разобрать задачи", "разобрать планы" or a very close equivalent, force a different main-goal category today;
- make the main goal concrete enough that the end-state by evening is obvious;
- avoid vague main goals like "разобраться с чем-то" or "закрыть один вопрос" without making the done-state legible;
- make both small goals concrete and distinct;
- make the second small goal usually the more alive one: creative, social, cultural, movement, language, or a specific outing;
- do not reuse the same small-goal category on adjacent days unless weather or schedule clearly forces it;
- if yesterday used cleanup/order as a small goal, avoid cleanup/order again today;
- avoid repeating default pairs like "прибраться + почитать" too often;
- do not simulate diversity by swapping synonyms while keeping the same underlying pattern for many days in a row;
- check prerequisite realism inside each small goal: do not tell Misha to "разобрать короткий список" unless the list clearly already exists; prefer self-contained actions like "выписать 3–5 хвостов и закрыть один";
- do not let a small goal become a reduced-size copy of the main goal; the supporting step should help the day, not duplicate the same type of action in miniature;
- on Thursday and Friday, add one short weekend-planning block with exactly one realistic nearby idea and one link;
- weekend-planning ideas must stay within sane Moscow-weekend scope: city event, short day trip, nearby town, estate, park, museum route, or comparable option — not flights or oversized travel;
- if a small goal depends on a list, notes, bookmarks, chat backlog, or another source that may not already be prepared, explicitly include the gather/create step instead of assuming it exists;
- if suggesting reading, name the exact text/book/chapter/article and include one direct link;
- if suggesting a film, name the exact film and include one direct link;
- if suggesting movement, give one concrete short practice or video and include one direct link;
- if suggesting music, name one concrete track/album/playlist direction and include one direct link;
- if suggesting a game, name one concrete game and include one direct link;
- if suggesting a walk, name the exact place, prefer a concrete destination from the user's starting area, and include a map or route link;
- on Thursday and Friday, add one short weekend-planning note with one realistic idea and one link;
- weekend ideas should stay within sane reach from Moscow: a city event, nearby town, short road trip, estate/park/museum route, or day trip like Vladimir, Kolomna, Zvenigorod, Sergiev Posad, Pereslavl-Zalessky, Tarusa, or Tula are in scope; flights and oversized travel are not;
- every recommendation that names a concrete thing must carry its link in the same sentence or bullet;
- in Telegram-facing daily briefs, prefer short inline markdown links with human labels instead of raw pasted URLs; use labels such as `[Яндекс]`, `[Google]`, `[маршрут]`, `[статья]`, `[трек]`, `[фильм]`, `[событие]`, or another natural object label that fits the sentence;
- avoid exposing long raw URLs in the final brief unless there is a specific reason the user asked for the literal URL text;
- if a route link is needed for Yandex Maps, prefer a coordinate-based route deeplink over an address-string route deeplink, because Telegram/Yandex handoff is more reliable with coordinates in this workflow;
- if the route itself is unreliable in Yandex, prefer giving a Google route link for the route and a separate Yandex place link only when needed, rather than pretending the Yandex route worked;
- keep leisure and support ideas lightweight: not "watch the whole film", not "read the whole book", not "listen to the whole album", but a small optional step for roughly 10–20 minutes unless the user explicitly asked for a bigger plan;
- treat overscoped leisure suggestions as a real quality failure, not a cosmetic one: a recommendation should feel easy to accept, not like another task to complete;
- avoid vague wording such as "почитать что-то", "куда-нибудь пройтись", or "сменить контекст";
- prefer leisure lead-ins that sound conversational: "Если захочется куда-то выбраться" or "Если будет настроение выйти";
- format links as short inline markdown labels inside the sentence, not as raw pasted URLs; prefer labels like [Яндекс], [Google], [статья], [трек], [фильм], [событие], [маршрут], or a short natural title;
- if the suggestion is a destination from Misha's home, prefer a route link over a plain map point;
- for Yandex route links from home, prefer coordinate-based `rtext` deep links rather than address-string route links when practical;
- if the generated text sounds too polished, symmetrical, or lifestyle-editorial, treat that as a quality failure and tighten toward shorter Telegram-native phrasing.
- explicitly ban generated micro-constraints and fake optimization language in user-facing Russian. By default, avoid constructions like `один мессенджер`, `одну почту`, `одно сообщение`, `одна мелочь`, `один вопрос`, `один слот`, `один блок`, `ровно 20 минут`, or similar count-based wording unless the number is genuinely important for meaning.
- if removing `один/одна/одно` still leaves an unnatural sentence, rewrite the whole recommendation instead of only swapping one word.
- avoid weak placeholder nouns when a normal everyday object can be named more directly: `вопрос`, `момент`, `история`, `хвост`, `штука`, `что-то важное`.
- weather phrasing must stay semantically clean: describe the weather first, then add at most one matching practical note. Do not glue unrelated ideas with fake cause-and-effect connectors like `так что`, `поэтому`, or `из-за этого`. Example of bad logic: `к вечеру возможен дождь, так что воду лучше взять`.
- weather retrieval must be source-verified, not snippet-verified. Search-result snippets, news rewrites of another forecast, and SERP previews are discovery only.
- for Moscow weather, first find a candidate forecast page, then fetch the actual page content with a tool that can read it directly (`terminal` with HTTP fetch, `browser_*`, or another raw page read). Do not present precise conditions like `облачно`, `дождь`, `+18…+23` as verified if they came only from snippet text.
- if direct page fetch fails, either keep the weather line explicitly lower-confidence (`по snippet-ам похоже...`) or simplify it to only what was actually confirmed. Do not quietly convert snippet hints into confident factual wording.
- when iterating on style, verify against one fresh generated brief at a time and report one verdict on that latest run. Do not show Misha a chain of multiple intermediate cron outputs as if they were parallel final candidates.

For leisure suggestions in Moscow:
- provide no more than one option;
- prefer a concrete current event over a generic venue page;
- omit the suggestion entirely if nothing clearly fits.

# Pitfalls

- Mistaking `manual run + scheduled run` for a scheduler bug.
- Testing against live Telegram delivery and then treating the extra message as a duplicate.
- Assuming that "test period" means local-only delivery for Misha. In this workflow, tests normally still go to Telegram unless he explicitly asks for silent/local mode.
- Creating a second cron job instead of refining the current one.
- Letting the brief drift into abstract self-help language.
- Using artificial phrases such as "сменить контекст" for leisure or small-step transitions.
- Repeating a concrete fallback object across different days while pretending the brief is varied. Typical failure mode: the wording changes, but the same nearby place or the same browser game comes back again.
- Using too short a recall window for repetition control, so the prompt only avoids yesterday's phrasing but still recycles the same concrete idea inside 1–2 weeks.
- Checking only categories (walk/game/article) instead of the specific object inside that category.
- Pasting long raw URLs into a Telegram-facing daily brief when a short inline markdown link would be cleaner and more readable.
- Using a Yandex route deeplink built from address strings when this workflow is more reliable with coordinate-based route links.
- Treating a map point link as an acceptable substitute when the user explicitly needed a built route.
- Turning small goals into a second and third major task.
- Bundling multiple actions into one "small" goal.
- Writing a small goal that assumes a prerequisite object already exists (for example, telling Misha to sort a list before the list has been created or gathered from notes/messages).
- Letting the main goal and a small goal collapse into the same action family, so the message repeats one idea at two scales instead of separating focus and support.
- On Thursday/Friday, giving no weekend look-ahead at all or suggesting unrealistic travel that does not fit a normal weekend from Moscow.
- Forcing a leisure recommendation every time, even when weather or relevance is weak.
- let the daily brief drift into polished lifestyle-copy wording instead of a short live Telegram message.
- letting the model escape one banned phrasing pattern only by replacing it with another generated count-based pattern such as `одно сообщение`, `одна мелочь`, `один денежный хвост`, or `одна партия`.
- fixing a bad `один/одна` sentence cosmetically instead of rewriting the whole recommendation in normal chat Russian.
- writing a weather line with a fake cause/effect bridge, for example `к вечеру возможен дождь, так что воду лучше взять`, where the practical note does not actually follow from the stated weather detail.
- when testing style refinements, showing the user several intermediate cron outputs and discussing them as if they were competing final versions instead of judging only the latest run.
- Pasting raw long URLs instead of hiding them under short inline labels.
- Linking a destination as a plain map point when the useful user action is actually a route from home.
- In a scheduled cron run, ending with a literal question or invitation to answer now (for example `Ок такой план?`, `или сегодня сам хочешь выбрать фокус?`). Cron delivery is one-way: the brief should feel complete as-is and must not pretend the agent is waiting for a reply.
- Reusing the same closing formula across several days just because the prompt once asked for a final question.
- In non-interactive cron contexts, treating the prompt's `final question` slot literally instead of converting it into a soft declarative close such as `Если захочешь, потом можно самому переопределить фокус дня.`
- Letting prompt instructions override delivery reality: if a cron prompt explicitly asks for a `final question`, the skill must win and the agent should convert that slot into a non-question close instead of following the prompt literally.
- Forcing a leisure recommendation every time, even when weather or relevance is weak.

# Verification checklist

Before declaring the task done, verify:
- the job exists in only one active version for that purpose;
- the recent-history scan is long enough to catch concrete-object repetition, not just adjacent-day wording repetition;
- the anti-repeat check was performed against the actual final texts of recent briefs, not only session_search snippets or prompt fragments;
- the weather line is backed by a directly fetched forecast page or is explicitly worded as lower-confidence when only snippets/news rewrites were available;
- the generated brief does not reuse the same concrete leisure/support object from the recent history window unless there is an explicit reason;
- the generated brief does not quietly reuse the same weekend-destination family or fallback support idea under slightly different wording;
- if the prompt was tightened to ban sticky fallback ideas, a manual rerun actually stops using them;
- links in Telegram-facing daily briefs are rendered as short inline markdown labels rather than raw pasted URLs;
- if the brief contains a route, the route link format actually matches the intended outcome (route vs point), and Yandex route links use coordinates where relevant;
- in scheduled cron delivery, the final line is a soft declarative close rather than a literal question, and the message does not end with a question mark unless the user explicitly asked for interactive wording;
- daily starts with `Доброе утро, Миша!`;
- daily has exactly 1 main goal and 2 small goals;
- weekly uses the compact 5-block structure;
- if a test job is succeeding, the plan for promotion is to extend that same job rather than revive a duplicate unless there is a specific reason.

# Support files

See `references/style-and-rollout.md` for concrete wording constraints and rollout notes from the May 2026 self-development cron refinement session.

See `references/concrete-anti-repeat-for-daily-briefs.md` for a concrete debugging pattern when users complain that the daily brief keeps reusing the same specific leisure/support ideas across different days.
