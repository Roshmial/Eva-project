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
   - Start exactly with `Доброе утро, Миша!`
   - Then one short factual line with day/date and weather only.
   - Weather line must explicitly include both: temperature and rain/no rain.
   - The structural contract is authoritative at the prompt/preflight level, not from this skill by itself.
   - If the current prompt says `1 main + 1 small`, follow that literally.
   - If the current prompt says `1 main + 2 small`, follow that literally.
   - Only when the prompt does not restate the structure may you fall back to the older default shape used in this stream.
   - Do NOT silently drift from the active contract into a mood note, day-description, event/no-event meta commentary, or reflective mini-message even if style tuning is underway.
   - After the weather line, the brief must still function as a daily plan with recommendations, not as an observation about the day.
   - Do NOT default to a rigid `Фокус дня:` rubric plus two symmetric bullets. That structure itself can make the text sound generated.
   - Prefer a short Telegram-style shape: one natural main-goal line, then exactly 2 useful support lines with genuinely different layers.
   - Use an explicit `Фокус дня:` label only if it genuinely improves clarity. If the label makes the text feel like a template or mini-plan, drop it.

   - Choose only what actually fits today's context. Do not force pre-trip bullets every time just because a trip is approaching.
   - The main thought should usually be the highest-value result of the day and concrete enough that by evening the result is visible.
   - The main thought is a goal axis, not a paraphrased action list and not a soft ban. Reject lines like `собрать внятный рабочий день`, `закрыть главное`, `довести до конца один важный рабочий кусок`, `пройти день ровно`, `не растаскивать себя`, or any other phrase that could be pasted into almost any weekday unchanged.
   - Also reject smoother variants that still carry the same emptiness, for example `оставить работу в собранном виде`, `спокойно войти в вечер`, `добить один заметный кусок`, or similar safe universal formulas.
   - Recommendations should support the day without sounding like a second full agenda.
   - Each recommendation must be one clear thing, naturally phrased, and realistically doable.
   - Recommendations must not be reduced-size copies of the main thought.
   - If the first recommendation already covers the trip/admin action, the next recommendation must add a genuinely different layer rather than rephrase the same storyline (`сверь билет` -> `оставь запас на сборы`) in softer words.
   - If a trip is mentioned, name it explicitly (`поездка в Волгоград`, `выезд`, `билет`) instead of hanging the action in the air.
   - Do not let the trip become the hidden center of the whole brief. If the main thought already leans toward departure logistics and one recommendation is also about the trip, the candidate should be rejected.
   - Do not skip prerequisites inside a recommendation: if the action assumes a list, source, or setup that may not exist yet, include that setup in the action itself.
   - Do not let recommendations drift into generic self-help wording or abstract framing.
   - Multimedia is optional, not mandatory. If the media suggestion is weak, random, or inserted only to satisfy variety, omit it.
   - In scheduled cron delivery, the final rendered brief must read as complete one-way output. If the prompt contains a slot like `one short final question`, reinterpret it as a soft closing line, not as a literal question to answer now.
   - Be extremely careful with prompt examples. Do not keep sample lines in the prompt unless they are genuinely good enough to be copied by the model. A bad example inside `good focus` or `good recommendation` lists acts like a poisoned training sample and will reappear in production output.
   - When iterating on quality for this user, do not report progress as success. Keep refining silently and only surface a status update when the brief is stably good across repeated reruns, not just one less-bad sample.

   - Treat this as a precedence rule, not as style advice: when the prompt's output structure says `one short final question`, the non-interactive delivery rule overrides that structure.
   - Default rule for non-interactive cron briefs: do not end with a question mark and do not ask `Ок такой план?`, `хочешь сам выбрать фокус?`, `норм так?`, `или сегодня у тебя свой фокус?`, `подходит такой расклад?`, or close variants.
   - Final pre-send check for cron briefs: inspect the actual rendered closing line. If it ends with `?` or invites an answer now, rewrite it before returning the message.

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
   - Internal route inputs such as exact home coordinates are implementation context only. Never expose them in the user-facing brief and never write as if Misha knows the hidden routing point or technical map setup.
   - If a route suggestion needs a destination, name the place like a normal human recommendation to a familiar person; do not surface the routing substrate.
   - Optional Moscow leisure suggestion: at most 1 concrete option with 1 link, only when it genuinely fits the day.
   - The user prefers the old compact Telegram shape, but wants usefulness preserved. Do not trade specificity away just to make the brief shorter.
   - Main and support lines should be concrete actions, not meta-advice about priorities, focus, motivation, primary causes, attention, context layers, or abstract self-management.
   - Good lines sound like: do a stretch, watch one short video, read one concrete text, clear one bag, answer one message, check one route. Bad lines sound like: reconsider a priority, inspect a focus layer, check what is truly important, revisit a pattern, or any other abstract management prose.
   - If a candidate line needs explanation to feel useful, it is probably not useful enough for this user.
   - Prefer a literal action with a visible finish state over an intelligent-sounding reflection.

8. Maintain a usefulness bank and dedupe it before every run.
   - Do not improvise the daily from vibes alone. Keep a curated bank of candidate useful actions.
   - Each bank item should be short, specific, and directly usable in a morning brief.
   - Before selecting today's lines, check recent outputs for both literal and semantic repetition.
   - If an idea already appeared recently, find a different idea, not a paraphrase of the same advice.
   - Repeated anchor objects like The Twelve-Factor App, Townscaper, Pomodoro, or other sticky fallback ideas should be explicitly banned when they start recurring.
   - Keep diversity at the idea level, not only at the wording level.

9. Validate the bank itself, not only the rendered brief.
   - Curated item lists drift toward pseudo-useful abstractions unless they are checked deliberately.
   - Run a lightweight validation pass over the bank to catch dead phrases, kantselyarizm, motivational filler, and lines that sound clever but do not tell the user what to do.
   - Treat bank cleanup as routine maintenance, not a one-time repair.
   - See `references/daily-usefulness-bank-and-validation.md` for a compact pattern: usefulness registry, semantic bans, validation heuristics, and prompt constraints that keep the short format concrete.

10. Weather wording must stay source-shaped and conservative.
   - For this user, weather lines should read like directly-fetched facts, not synthesized confidence.
   - Prefer wording grounded in what the fetched page explicitly exposes right now (`сейчас +17 °C, переменная облачность`) plus at most one cautious forward note (`днём до +20 °C`, `дождь возможен`).
   - Avoid over-assertive summary phrasing when part of the line is inferred from hourly blocks rather than stated verbatim on the source page.

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

6. When repeated prompt-level edits stop sticking, split the runtime into stages instead of growing one monolithic spec.
   - Separate context gathering, candidate generation, criticism/quality gate, and fallback into distinct files or explicit stages.
   - The cron prompt should sequence those stages directly rather than asking one pass to do everything at once.
   - Treat this as the default escalation path when Misha says the issue is already in the pipeline, not in one more wording rule.
   - If prompt healing keeps producing new dead phrases, move more logic into cron structure itself: let a preflight script emit day anchors, task families, suggested raw tasks, and reject hints.
   - For high-sensitivity daily briefs, prefer a bank-first contour: task-picker -> line bank -> line-writer -> critic -> final editor -> reject list.
   - In that contour, the agent-layer should mostly render and reject, not re-decide the day's logic from scratch.
   - After a structural rewrite, do not declare success from one good run. Do a same-date rerun series and check whether wording drifts for no real reason.
   - If the same day reruns keep wobbling, move stability into preflight too: emit a same-date baseline and explicit reuse rules so the renderer prefers stable wording over fake novelty.
   - For cross-day repetition, do not rely only on wording bans. Make preflight inspect recent distinct-day outputs, classify the task-family mix, and rotate small-goal families when the same combination keeps repeating across соседние дни.
   - If the user explicitly says to kill the current architecture and rebuild from scratch, stop doing micro-edits on the existing contour. Replace the old staged/prompt bank with a simpler fresh contract and verify that contract directly on a live run.
   - In that reset mode, rebuild the bank around literal action lines first. The quality bar is not `sounds thoughtful`; it is `reads like a direct thing to do today`.
   - Treat `good idea = сделай ...` as a hard filter. Reject lines about priorities, focus, importance, attention, layers, causes, or other meta-management prose even when they sound intelligent.
   - In that reset mode, prefer a small curated bank of concrete main/self-development items and support items with built-in links over abstract placeholder families like `work text`, `close one thing`, or other generic work-safe defaults.
   - Rebuild the selector around explicit action families. Main and support lines must come from different families; anti-repeat is not only across previous days, but also inside the same rendered brief.
   - For linked suggestions, store the markdown link directly inside the curated bank line and mark it as link-bearing in preflight. The renderer should preserve the selected line almost verbatim instead of re-attaching URLs later.
   - When the renderer drifts on date/day wording, move that field into preflight too: emit a ready `DAY_LINE_RENDERED` string and make the final prompt copy it verbatim rather than translating or reconstructing it.
   - If the user resets the contract itself, follow the new contract literally even when it replaces the previous default. In particular, this user may explicitly switch daily from `1 main + 2 small` to `1 main self-development + 1 smaller support task`; after that switch, continuing to enforce the older 3-task shape is a mistake.
   - Treat prompt-provided authoritative fields as an implementation contract, not as style hints. If preflight already provides `DAILY_CONTEXT.today`, `DAILY_CONTEXT.weekday`, `WEATHER_SOURCE.weather_line`, `SELECTED_MAIN`, or `SELECTED_SMALL`, do not paraphrase or recompute those fields unless the prompt explicitly allows replacement.
   - If preflight/prompts already provide fully rendered fields like `DAY_LINE_RENDERED`, `SELECTED_MAIN_RENDERED`, or `SELECTED_SMALL_RENDERED`, copy those lines literally by default. Do not "improve" them into a nicer-sounding variant, do not swap the concrete object, and do not add a different explanation line just because it sounds more natural.
   - When the prompt says `строки 3 и 4 не перепридумывай`, treat any semantic rewrite as a hard failure even if the new line still looks good in isolation. Only tiny grammar fixes are allowed, and only when the prompt explicitly permits them.
   - Prompt examples are poison unless they are dynamically aligned with the same authoritative fields. If the format line contains a static sample like `Четверг, 6 августа`, rewrite the prompt before trusting any rendered output; otherwise the renderer may copy the stale example literally.
   - Acceptance requires an exact-contract check on the rendered artifact itself: line count, date/day match against preflight, weather line source fidelity, task-count shape, and literal match against provided `*_RENDERED` lines when the contract says to preserve them. A superficially good sample is still a failure if any one of those contract fields drifted.
   - When external links are part of the contract, prefer embedding them into the existing object phrase (`[предисловие SICP]`, `[Townscaper]`, `[ВДНХ]`) instead of appending detached labels like `книга`, `маршрут`, or `статья` at the end of the line.
   - Once the user says `доведи только качество`, stop revisiting architecture and work only on the editorial quality of the curated content bank and final edit pass.
   - Editorial quality failures for this user include methodical phrasing like `выписать 3 мысли`, `записать 3 наблюдения`, `отметить один принцип`, and soft artificial lead-ins like `если захочется коротко переключиться` when a simpler sentence lands better.
   - Also reject soft service-y tails like `до сих пор правда полезно`, `проветрить голову`, `без обязательств`, `если понадобится, вот метод`, or similar gentle filler that sounds correct but not alive.

7. For Misha's morning daily, preserve the active hard output contract even during style repairs.
   - The brief is still a plan, but its exact shape comes from the current prompt/preflight contract.
   - Do not let a style-debugging pass drift into atmospheric notes, meta-commentary about the day, or abstract mood-setting.
   - A structurally correct but lifeless brief is still a failure.
   - After picking the best candidate, run one more edit pass focused only on liveliness and density.
   - If the chosen line is merely a shortened bad line, reject it and go back to another candidate.
   - If Misha says `под ключ` and gives a quality bar, do not stop at `already much better`; keep iterating until that bar is actually met or a real blocker appears.
   - Personal-event anchors about Misha himself must stay user-facing. Never render them in third person like `день рождения Михаила`; normalize them to direct phrasing such as `завтра день рождения`.
   - Do not ban natural live Telegram frames like `я бы` or `можно` at the preflight ban-list layer. Ban dead formulas, not the grammatical voice that keeps the brief human.
   - See `references/august-2026-daily-plan-quality.md` for the August 2026 corrections on event-centric framing, pseudo-productivity wording, and water control.

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
- do not stop at session_search snippets. Snippets are only discovery. Before drafting, extract the final assistant text for the last 10 real morning briefs and make a compact working list of: main-goal category, support categories, concrete objects/places/media/games, and weekend idea.
- when searching recurring cron outputs, do not rely on naive FTS queries that mostly hit the prompt text itself (`Доброе утро, Миша`, `morning message`, `okay with this plan`, etc.). Prefer a title-first path: browse recent sessions, identify the exact cron session ids for the job, then read those sessions or scroll around the assistant closeout message.
- if a session_search discovery query mostly returns the user's prompt/instructions instead of the delivered brief text, treat that as a retrieval failure, not as evidence that repetition checking is done.
- only fall back to direct SQLite/terminal inspection of the Hermes session DB after session_search title/session-id retrieval has proven insufficient. Do not jump to ad-hoc DB queries just because the first keyword search was poorly chosen.
- if the retrieval path only surfaced snippets or mixed prompt text, treat the anti-repeat check as incomplete and keep digging until the actual final brief texts are visible.
- treat both wording repetition and idea repetition as real failures, not cosmetic issues;
- explicitly track repeated concrete objects, not just categories: the same place, the same game, the same article/video/media item, the same weekend-destination family, or the same fallback micro-activity still counts as repetition even if the wording changes;
- repetition control is broader than the recent brief texts alone. Also check the current conversation and very recent session context for places, routes, media, venues, products, or concrete recommendations that were already discussed with Misha.
- if a place or concrete recommendation was just discussed in chat yesterday or earlier that same day, treat it as already socially "used" for recommendation purposes, even if it never appeared in the last generated daily brief.
- use a practical anti-repeat window of roughly the last 2–3 days for place/route/venue suggestions. Inside that window, do not present the same city route, walk, restaurant, venue, or concrete place as a fresh recommendation unless there is a real new reason.
- for geographic recommendations, wording changes do not count as novelty. If the useful anchor is still the same place or the same route family, it is still a repeat.
- this is not only a travel rule. Apply the same continuity check to ordinary recommendations too: routes, cafes, videos, music, films, events, admin actions, and small-life suggestions.
- when the user likely already acted on yesterday's advice, prefer either a different recommendation or no recommendation, rather than repeating the old one with slightly different wording.
- treat repeating the same concrete place or the same concrete game within roughly 14 days as a hard failure unless the user explicitly asked to revisit it;
- if a concrete suggestion appeared recently, force a different category instead of paraphrasing the same idea again;
- for known sticky fallback ideas, it is acceptable to name them explicitly in the prompt as temporary bans until the rotation stabilizes;
- do not repeat the same main-goal category on adjacent days;
- if yesterday or the day before used "навести порядок в делах", "разобрать задачи", "разобрать планы" or a very close equivalent, force a different main-goal category today;
- make the main focus concrete enough that the end-state by evening is obvious;
- avoid vague main-focus phrases like "разобраться с чем-то" or "закрыть один вопрос" without making the done-state legible;
- keep recommendation wording short and plain;
- explicitly ban filler or generated phrasing such as `обычный день`, `можно держать ритм`, `поддерживающая вещь`, `конкурентный рабочий результат`, `держать в голове`, `хвосты`, `ветки`, and close variants;
- explicitly ban empty soothing phrasing such as `выдохнуть к вечеру`, `чтобы не висело в фоне`, `собрать день`, `пройти день ровно`, `закрыть главное`, `довести до конца один важный рабочий кусок`, and close variants;
- explicitly ban unnecessary qualifier tails such as `без распыления`, `без перегруза`, `без лишнего`, `не расползаясь`, `без длинного выезда через весь город`, `без лишней логистики`, or close defensive padding;
- if removing a qualifier tail leaves the same recommendation value, prefer the shorter sentence;
- recommendations may include work, trip prep, music, film/series/video, a walk, a nearby route, an event, household reset, admin tasks, or rest; pick only what actually fits today's day type and energy;
- task lines must be compact and dense. If a line can be shortened by roughly a third without losing the action, rewrite it before delivery;
- ban watery lead-ins and explanatory tails in task lines, such as `на сегодня предлагаю`, `оставить себе`, `по действительно важной теме`, `которое потом уже...`, `чтобы день закончился...`, `пока сухо и не жарко`, and close variants;
- for a normal workday with no strong external hook, still produce real tasks; do not replace them with day classification or atmosphere-only wording;
- do not force the same recurring pre-trip checklist when the day would benefit more from leisure, recovery, or cultural suggestions;
- keep support ideas varied and human: examples include `послушай что-то новое`, `выбери короткую прогулку`, `посмотри вечером один фильм`, `проверь билеты и брони`, `докупи что нужно`;
- if suggesting reading, name the exact text/book/chapter/article and include one direct link;
- if suggesting a film, name the exact film and include one direct link;
- if suggesting movement, give one concrete short practice or video and include one direct link;
- if suggesting music, name one concrete track/album/playlist direction and include one direct link;
- if suggesting a game, name one concrete game and include one direct link;
- if suggesting a walk, name the exact place, prefer a concrete destination from the user's starting area, and include a map or route link;
- on Thursday and Friday, add one short weekend-planning note with one realistic idea and one link;
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
- explicitly ban generated micro-constraints and fake optimization language in user-facing Russian. By default, avoid constructions like `один мессенджер`, `одну почту`, `одно сообщение`, `одна мелочь`, `один вопрос`, `один слот`, `один блок`, `ровно 20 минут`, `20–30 минут`, `полчаса`, `10–15 минут`, or similar count-based wording unless the number is genuinely important for meaning.
- avoid stale work-trope wording that reads like generated planning prose: `текст с правками`, `добить`, `дожать`, `не добивать`, `закрыть тему`, `короткий рабочий текст`, and close variants when they are only generic placeholders rather than real context.
- avoid service-template phrasings that read like generated planning prose: `главный рабочий блок`, `собрать базу`, `отдельно собрать`, `подойдёт`, `переключить голову`, and close variants.
- if a sentence explains the recommendation instead of simply offering it, shorten it.
- keep recommendations slightly uneven in a human way; a little live Telegram roughness is better than polished symmetry.
- restore old-logic richness when useful: besides tasks and trip prep, daily briefs may include concrete links to a route, music, a YouTube video, a film/series item, or one fitting event.
- before returning the final brief, do one internal rewrite pass focused only on delivery texture: cut decorative glue, remove `..., без ...` and `..., а не ...`, remove over-explanation, and prefer the shorter more natural version when both mean the same thing.
- also ban unnecessary qualifier tails that do not materially change the recommendation. Cut endings like `без длинного выезда через весь город`, `без лишней логистики`, `если не хочется усложнять`, or close variants when they only add defensive padding rather than useful guidance.
- if removing a qualifier tail leaves a simpler sentence with the same decision value, prefer the shorter sentence.
- if removing `один/одна/одно` still leaves an unnatural sentence, rewrite the whole recommendation instead of only swapping one word.
- avoid weak placeholder nouns when a normal everyday object can be named more directly: `вопрос`, `момент`, `история`, `хвост`, `штука`, `что-то важное`.
- weather phrasing must stay semantically clean: describe the weather first, then add at most one matching practical note. Do not glue unrelated ideas with fake cause-and-effect connectors like `так что`, `поэтому`, or `из-за этого`. Example of bad logic: `к вечеру возможен дождь, так что воду лучше взять`.
- weather retrieval must be source-verified, not snippet-verified. Search-result snippets, news rewrites of another forecast, and SERP previews are discovery only.
- for Moscow weather, first find a candidate forecast page, then fetch the actual page content with a tool that can read it directly (`terminal` with HTTP fetch, `browser_*`, or another raw page read). Do not present precise conditions like `облачно`, `дождь`, `+18…+23` as verified if they came only from snippet text.
- if `web_extract` reports an environment limitation such as `DuckDuckGo (ddgs) is a search-only backend and cannot extract URL content`, treat that as a routing failure, not as partial success. Immediately pivot to `terminal`/`curl`, `browser_*`, or another direct fetch path in the same run.
- after such an extract failure, do not keep stacking more `web_search` calls and then synthesize the weather line from snippets. That is still snippet-level evidence.
- if no direct fetch path works, either keep the weather line explicitly lower-confidence (`по snippet-ам похоже...`) or simplify it to only what was actually confirmed. Do not quietly convert snippet hints into confident factual wording.
- for repeated reruns on the same calendar date, weather stability is more important than fresh rewording. If an earlier same-date brief already had a clean weather line and no stronger direct source contradicted it, keep that line verbatim instead of drifting between versions across manual tests.
- when iterating on style, verify against one fresh generated brief at a time and report one verdict on that latest run. Do not show Misha a chain of multiple intermediate cron outputs as if they were parallel final candidates.
- on style-tuning passes, do not stop after a single improved run. Manual reruns on the same date are part of verification; acceptance needs a short stable streak, not one lucky candidate.
- treat dry task-manager phrasing as a hard failure even when the structure is technically correct. Lines like `ответы, календарь и мелкие дела`, `финальные правки и короткие задачи`, or other category-lists usually mean the brief still sounds generated.
- for travel-day briefs, mentioning the trip once is enough. If one line already covers `билет / время выезда / дорога`, the remaining lines must live in another layer of the day.

For leisure suggestions in Moscow:
- provide no more than one option;
- prefer a concrete current event over a generic venue page;
- omit the suggestion entirely if nothing clearly fits.

# Pitfalls

- Mistaking `manual run + scheduled run` for a scheduler bug.
- Testing against live Telegram delivery and then treating the extra message as a duplicate.
- Assuming that "test period" means local-only delivery for Misha. In this workflow, tests normally still go to Telegram unless he explicitly asks for silent/local mode.
- Leaving Telegram streamed delivery enabled when the failure pattern is specifically edit-based (`Message to edit not found`, suppress-normal-final-send, flood-control around streamed sends). In that case, disable streaming on the Telegram platform layer first instead of broad global shutdown.
- Creating a second cron job instead of refining the current one.
- Letting the brief drift into abstract self-help language.
- Letting style-fix work accidentally erase the original job contract (`1 main goal + 2 small goals`) and turn the brief into a mood note or commentary about the day.
- Letting `normal workday` handling collapse into meta lines like `обычный рабочий день`, `без отдельного внешнего сюжета`, or other service-style day classification instead of real recommendations.
- Allowing watery formulations where the action could be said much shorter.
- Using artificial phrases such as "сменить контекст" for leisure or small-step transitions.
- Adding defensive qualifier tails that sound generated rather than helpful, such as `без длинного выезда через весь город`, `без лишней логистики`, or close variants when the shorter sentence already says enough.
- Repeating a concrete fallback object across different days while pretending the brief is varied. Typical failure mode: the wording changes, but the same nearby place or the same browser game comes back again.
- Using too short a recall window for repetition control, so the prompt only avoids yesterday's phrasing but still recycles the same concrete idea inside 1–2 weeks.
- Checking only categories (walk/game/article) instead of the specific object inside that category.
- Pasting long raw URLs into a Telegram-facing daily brief when a short inline markdown link would be cleaner and more readable.
- Using a Yandex route deeplink built from address strings when this workflow is more reliable with coordinate-based route links.
- Treating a map point link as an acceptable substitute when the user explicitly needed a built route.
- Turning recommendations into a fixed checklist instead of a dynamic daily mix.
- Letting generated filler or defensive qualifier tails survive into the final text, for example `обычный день`, `можно держать ритм`, `конкурентный рабочий результат`, `без распыления`, `без перегруза`, or close variants.
- Overfitting the brief to trip-prep/admin bullets and forgetting that some days should instead suggest music, film, a walk, an event, or a simpler evening plan.
- Turning recommendations into a second and third major task.
- Bundling multiple actions into one "small" goal.
- Writing a recommendation that assumes a prerequisite object already exists (for example, telling Misha to sort a list before the list has been created or gathered from notes/messages).
- Letting the main focus and a recommendation collapse into the same action family, so the message repeats one idea at two scales instead of separating focus and support.
- Allowing a positive-sounding focus line that is still semantically empty or portable across almost any weekday.
- Keeping bad examples inside the cron prompt under labels like `good focus`, `good phrasing`, or `good level`; the model will copy them back into production output.
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
- same-date reruns keep one stable weather line unless a stronger directly fetched source clearly forces a change;
- at least one post-weather line sounds like a normal human message rather than a category-list or mini task manager;
- if the day includes travel context, the trip is mentioned at most once unless there is a real same-day logistical reason for a second mention;
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

See `references/natural-telegram-digest-edit-pass.md` for a final wording pass that strips generated phrasing and restores a more live Telegram texture.

See `references/focus-vs-recommendation-and-poisoned-examples.md` for the specific failure mode where bad prompt examples poisoned production daily output and where focus/recommendation layers collapsed into the same storyline.

See `references/july-2026-same-date-rerun-stability.md` for same-date rerun discipline: weather stability, anti-task-manager filtering, and acceptance only after a short stable streak of good daily outputs.

See `references/staged-runtime-and-telegram-streaming.md` for the escalation pattern where repeated daily-brief prompt edits stop working, the runtime is split into generator/critic/fallback stages, and Telegram streaming is disabled at the platform layer to stop edit-based delivery failures.

See `references/august-2026-link-aware-daily-reset.md` for the reset-mode rebuild contract where the daily bank is recreated from zero, ideas are grouped by action family, link-bearing items are stored inline, and preflight emits `DAY_LINE_RENDERED` / `SELECTED_*_RENDERED` fields so the renderer copies instead of improvising.

See `references/august-2026-daily-structure-and-stability.md` for the next escalation step: moving day anchors, task families, suggested raw tasks, and same-date stability baselines into preflight so the agent mostly renders instead of re-deciding the day.
