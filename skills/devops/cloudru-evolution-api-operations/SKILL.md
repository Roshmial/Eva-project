---
name: cloudru-evolution-api-operations
description: "Use when operating Cloud.ru Evolution by API."
triggers:
  - User asks to verify Cloud.ru API access, list resources, or operate Cloud.ru Evolution VMs/networks by API.
  - You have Cloud.ru API credentials and a project_id, and need a minimal read-first operational path.
  - You need to move from docs to a live probe without guessing the wrong API host.
---

# Purpose

This skill is for practical Cloud.ru Evolution work when the goal is to prove API connectivity quickly, discover the correct service endpoint, and perform low-risk operational reads before any mutations.

# Core rules

1. Split the work into three layers.
   - Auth: prove the key works and obtain a bearer token.
   - Discovery: identify the exact service host from the service OpenAPI, not from memory or guessed console paths.
   - Project-scoped probe: perform one read-only call with `project_id` and only then move to resource-specific operations.

2. Prefer the documented service host over guessed domains.
   - Cloud.ru console paths and registry endpoints are easy to guess wrong.
   - For Evolution Compute and Evolution VPC, first read the service API page and extract the downloadable OpenAPI spec link.
   - Use the `servers:` block in that OpenAPI as the source of truth for the base URL.

3. Default sequence for a new contour.
   - Get bearer token.
   - Confirm `project_id`.
   - List VMs or VPC resources with one read-only request.
   - If needed, read the exact VM by `vm_id`.
   - Only after that consider `set-power`, password reset, or remote console actions.

4. Treat remote console as a separate access path from SSH.
   - A VM may be healthy and reachable through VNC/remote console while SSH from the internet still fails.
   - Do not conflate `VM is alive` with `SSH is reachable`.

# Known live pattern from this session

For Cloud.ru Evolution Compute docs, the VM service OpenAPI exposed:
- base host: `https://compute.api.cloud.ru`
- VM list path: `GET /api/v1/vms`
- VM detail path: `GET /api/v1/vms/{vm_id}`
- power control path: `POST /api/v1/vms/{vm_id}/set-power`
- password set path: `POST /api/v1/vms/{vm_id}/set-password`

For Evolution VPC docs, the OpenAPI exposed:
- base host: `https://vpc.api.cloud.ru`
- VPC list path: `GET /v1/vpcs?projectId=<PROJECT_UUID>`
- note: this VPC API uses `/v1/...` paths and camelCase query params such as `projectId`, unlike the Compute-style `/api/v1/...` shape

For VM create in a public-only contour, a live-safe pattern was confirmed:
- VM create path: `POST https://compute.api.cloud.ru/api/v1.1/vms`
- `interfaces[].type` may be `direct_ip`
- for `direct_ip`, the request must also include either `new_external_ip: true` or `attach_external_ip_id` / `attach_external_ip_name`
- omitting that extra field returns `422` with `Direct IP is allowed either with new_external_ip or attach_external_ip_id/attach_external_ip_name`
- this lets you create a VM with a direct public IP and no VPC/subnet attachment when the user explicitly wants to skip the private-network step

See `references/cloudru-evolution-live-probe.md` for the concrete probe pattern and findings.
See `references/cloudru-evolution-vpc-and-vm-create-notes.md` for VM-create, direct-IP, disk-attach, and subnet-resolution notes from a live project.

# Minimal working flow

## 1. Auth

Use:
- `POST https://iam.api.cloud.ru/api/v1/auth/token`
- JSON body: `{"keyId":"...","secret":"..."}`

Success condition:
- HTTP 200
- response contains `access_token`

## 2. Read VM list for a project

Use the bearer token against Compute:
- `GET https://compute.api.cloud.ru/api/v1/vms?project_id=<PROJECT_UUID>`

Practical note:
- guessed hosts like `https://api.cloud.ru/api/v1/vms` can be blocked or wrong for this operation even when auth works.
- use `compute.api.cloud.ru` when the spec says so.

## 2a. Read VPCs before assuming subnet names exist across zones

Use the bearer token against VPC:
- `GET https://vpc.api.cloud.ru/v1/vpcs?projectId=<PROJECT_UUID>`

Then use Compute for subnet enumeration:
- `GET https://compute.api.cloud.ru/api/v1/subnets?project_id=<PROJECT_UUID>`

Practical note:
- the default VPC can exist even when the expected default subnet for a specific AZ does not.
- do not assume `Default_ru.AZ-1` exists just because `Default_ru.AZ-2` exists.
- if the user specifies an exact CIDR and AZ inside the same VPC, verify first that the CIDR is not already occupied by another subnet in that VPC.


Once the list returns an item, extract `vm_id` and call:
- `GET https://compute.api.cloud.ru/api/v1/vms/<VM_ID>`

Useful fields to inspect early:
- `name`
- `state`
- `guest_agent_state`
- `availability_zone`
- `flavor`
- `image`
- `metadata_fields`
- `remote_console_url`
- `remote_console_ws`

## 4. Read interfaces and public exposure

Useful follow-up reads:
- `GET /api/v1/interfaces?project_id=<PROJECT_UUID>&vm_ids=<VM_ID>`
- `GET /api/v1/floating-ips?project_id=<PROJECT_UUID>`
- `GET /api/v1/security-groups?project_id=<PROJECT_UUID>`

This lets you separate:
- VM state
- network attachment
- floating IP state
- security group rules

## 4a. VM create shortcut when the user wants only a public IP

When the user explicitly says to skip VPC/subnet work and keep only a public IP:
- use `POST /api/v1.1/vms`
- set `interfaces` to a single item with:
  - `type: direct_ip`
  - `new_external_ip: true`
  - security group by name or id if needed
- keep the root disk in the `disks` block as a new `40 GB SSD` disk
- pass login/password/public key through `image_metadata`

This is a practical fallback when an exact subnet/AZ/VPC requirement is blocked by CIDR conflicts or missing default subnets.

## 5. SSH triage when VM is running but port 22 times out

If:
- VM state is `running`
- security group shows inbound `tcp/22`
- public IP is present
- but TCP/22 from outside times out

then treat it as an SSH reachability incident, not an API incident.

Check in this order:
1. Does the VM expose a public interface / floating IP?
2. Does the security group allow `tcp/22` from the needed source?
3. Is `sshd` running inside the guest?
4. Is port 22 actually listening inside the guest?
5. Is host firewall blocking (`ufw`, `iptables`, `nft`)?
6. Is the public NIC inside Linux actually up and configured?
7. Is there a deeper network constraint outside SG?

Prefer using remote console for the in-guest checks when SSH is not reachable.

### Guest-side direct-IP recovery pattern

A live failure pattern from this session:
- Cloud.ru shows the public `direct_ip` as attached and `in_use`.
- The security group on that public interface allows inbound TCP.
- Inside Linux, the public-facing extra NIC exists but is `DOWN`.
- Result: SSH/HTTP/HTTPS from outside all time out even though the VM is `running`.

Use this guest-side diagnostic sequence:
- `sudo ip a`
- `sudo ip r`
- `sudo ss -lntp`
- `sudo nft list ruleset`
- `sudo iptables -S`
- `sudo ufw status verbose`

If the public NIC is present but `DOWN`, a practical recovery sequence is:
- `sudo ip link set <public_nic> up`
- `sudo dhclient <public_nic>`
- then re-check `sudo ip a`
- and `sudo ip r`

After DHCP, explicitly inspect routing.
A second common failure pattern is dual default routes:
- one default via the private subnet NIC
- one default via the public NIC

That can produce asymmetric routing: ingress arrives on the public interface, but replies leave through the private default route. If services are listening and the public NIC is already up, inspect route preference/metrics next.

# Pitfalls

- Pitfall: proving auth and then calling guessed console or generic API hosts.
  Fix: derive the service base URL from the service OpenAPI `servers:` block.

- Pitfall: treating `404` on a guessed endpoint as evidence the key or API is broken.
  Fix: first confirm token issuance, then verify the correct service host.

- Pitfall: assuming the VPC API follows the same path shape as Compute.
  Fix: for VPC, check the spec and use `/v1/...` with the documented query params such as `projectId`.

- Pitfall: creating a `direct_ip` interface without `new_external_ip` or an attached existing external IP.
  Fix: for public-only VM creation, include `new_external_ip: true` or explicitly attach an existing public IP; otherwise Compute returns `422`.

- Pitfall: assuming `POST /api/v1/vms/{vm_id}/remote-console` will immediately return the console URL in the same response body or populate `remote_console_url` on the next VM read.
  Fix: treat the endpoint as a trigger-only `204` operation; if console automation is needed, be ready to obtain the actual console URL by a different live path instead of assuming the field will appear in VM detail immediately.

- Pitfall: assuming a default subnet exists in every AZ, or trying to recreate the same CIDR in the same VPC for another AZ without checking collisions.
  Fix: list subnets first, verify the target subnet by name/AZ/CIDR, and expect `409 subnet_already_exists_in_vpc` when the CIDR is already present in that VPC.


# References

- `references/cloudru-evolution-live-probe.md` — concrete endpoint and troubleshooting notes from a live project-scoped probe.
