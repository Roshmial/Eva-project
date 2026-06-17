# Hermes Web personalization / memory live verification

Use this when a user says memory is disabled, forgotten, or mixed across users.

## Evidence ladder

1. DB row exists for the target user.
2. `pinned_json` / `assistant_profile_json` / `goals` / `constraints_text` are populated as expected.
3. Backend code still builds personalization through:
   - `user_to_dict(...)`
   - `build_personalization_block(...)`
   - `build_hermes_system_prompt(...)`
4. Recent assistant messages for that same user show:
   - `personalization_used`
   - `personalization_preview`
   - `downstream`
5. Result is classified as:
   - global failure
   - route-specific bypass
   - stale user data
   - agent text mismatch

## Strong indicators

### Memory is working
- DB fields populated
- recent assistant message has `personalization_used=true`
- `personalization_preview` contains user-specific fields such as goals, constraints, pinned memory, tone, role, team

### Memory is not proven on this route
- `personalization_used=false`
- `personalization_preview=dashboard-route` or similar route marker
- `downstream` points to dashboard / research / attachment path

This does not prove memory is globally off.

## Useful fields to surface in reports

- user id / email
- role
- timezone
- goals
- constraints
- pinned memory list
- assistant profile block
- recent message id / thread id
- `personalization_used`
- `personalization_preview`
- `downstream`

## Recommended wording

- "Память в prod для этого пользователя есть в базе и используется в обычном agent-path."
- "Фраза про отключённую память не подтверждается как глобальное состояние."
- "С высокой вероятностью это special route, где personalization не применяется или не отражается так же, как в основном chat-path."

## Practical note

If login under old demo credentials fails, do not burn time retrying the same probe. Switch to direct server verification:
- inspect running service interpreter
- inspect live DB with the same runtime Python/venv
- inspect recent message metadata for the user
