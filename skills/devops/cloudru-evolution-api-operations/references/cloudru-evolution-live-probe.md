# Cloud.ru Evolution live probe notes

Session pattern captured from a real project-scoped probe.

## Auth

Working auth endpoint:
- `POST https://iam.api.cloud.ru/api/v1/auth/token`
- body: `{"keyId":"...","secret":"..."}`

Observed success shape:
- HTTP `200`
- fields included `access_token`, `id_token`, `expires_in`

## Service host discovery

Do not guess the compute base URL from generic console or registry paths.

Working method:
1. Open the service docs page.
2. Extract the downloadable OpenAPI spec URL.
3. Read `servers:` from the spec.

Observed results:
- Virtual Machines spec -> `https://compute.api.cloud.ru`
- Evolution VPC spec -> `https://vpc.api.cloud.ru`

A guessed call to `https://api.cloud.ru/api/v1/vms?...` returned a blocked/403 HTML page, while the documented `compute.api.cloud.ru` endpoint worked.

## Compute probe that worked

Project used in the live probe:
- `project_id = 6649fb7f-140c-401a-9420-16948b8aa5aa`

Working read-only calls:
- `GET https://compute.api.cloud.ru/api/v1/vms?project_id=<PROJECT_ID>`
- `GET https://compute.api.cloud.ru/api/v1/vms/<VM_ID>`
- `GET https://compute.api.cloud.ru/api/v1/interfaces?project_id=<PROJECT_ID>&vm_ids=<VM_ID>`
- `GET https://compute.api.cloud.ru/api/v1/floating-ips?project_id=<PROJECT_ID>`
- `GET https://compute.api.cloud.ru/api/v1/security-groups?project_id=<PROJECT_ID>`

Observed VM example:
- `name = vm-training`
- `vm_id = e6be7ec8-3eb3-4f86-883d-190d48f3462e`
- `state = running`
- `guest_agent_state = enabled`
- image `ubuntu-22.04`
- flavor `low-2-4`
- AZ `ru.AZ-1`

Observed network example:
- public IP / floating IP: `176.123.161.231`
- interface type: `direct_ip`
- SG allowed inbound `tcp/22`

## Remote console pattern

From VM detail, the API returned remote console fields:
- `vnc_url`
- `vnc_ws`
- `remote_console_url`
- `remote_console_ws`
- `remote_console_protocol = vnc`

Using the returned VNC URL in Hermes browser tools opened `noVNC` successfully.

What the live console proved:
- the guest OS was up
- login prompt existed
- login as `user1` succeeded
- the guest reached a normal Ubuntu shell/login state

## SSH triage lesson

In this probe, SSH from the external contour timed out even though:
- VM was `running`
- floating IP existed
- SG had inbound `22/tcp`
- remote console worked

Interpretation:
- API/auth path was healthy
- VM lifecycle path was healthy
- guest itself was alive
- the remaining issue belonged to SSH reachability, not to Cloud.ru API connectivity

Use remote console next for in-guest checks:
- `systemctl status ssh`
- `ss -tulpn | grep :22`
- `ip a`
- `ip r`
- `ufw status` or firewall equivalent

## Practical caution

When the user explicitly approves a temporary key for a bounded probe, it is acceptable to:
1. warn once,
2. perform the smallest read-only connectivity check,
3. confirm whether the API and target contour are alive,
4. then recommend key rotation.

Do not keep blocking on the security lecture after the user has explicitly chosen the bounded test path.
