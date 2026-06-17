# Secondary Telegram profile for closed chats

Use this pattern when Misha needs to read a closed group/channel without exposing Telegram API secrets in chat and without disturbing the existing production session.

## Core rule

Access to a closed chat is determined by the Telegram account's membership in that chat, not by creating a new Telegram application.

So for a closed chat you usually need:
- the same existing `TG_API_ID` / `TG_API_HASH` is fine;
- a different Telegram account if the current one is not a member;
- a separate Telethon session file;
- a separate Hermes/TG-API profile name.

## Safe setup pattern

1. Keep `profile_1` untouched.
2. Create a new profile name, for example `profile_private` or `profile_closed_groups`.
3. Provide `TG_API_ID` / `TG_API_HASH` only through a local env file or local shell environment.
4. Run `login.py` locally and enter phone/code/2FA only in the local terminal.
5. Save the new session as `session/<profile>.session`.
6. Verify chat access with Telethon before adding the profile to any recurring pipeline.

## Important distinctions

- New profile: usually yes.
- New session file: yes.
- New Telegram account: only if the existing account does not belong to the closed chat.
- New Telegram application (`api_id` / `api_hash`): usually no.

## Practical verification target

When checking a closed `t.me/c/.../...` link, first derive:
- internal raw id from the URL;
- candidate chat id as `-100<raw_id>`;
- target message id from the trailing segment.

Then test whether the session can:
- resolve the chat entity;
- read the specific message;
- read the latest N messages.

If entity lookup fails, the durable conclusion is not "the link format is unsupported" but "this session/account does not currently have chat access".
