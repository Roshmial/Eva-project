---
name: cloudru-load-balancer-diagnostics
description: "Use when Cloud.ru LB public/private exposure is unclear."
triggers:
  - User says a Cloud.ru load balancer has an external/public IP but traffic does not reach backend VMs.
  - LB name or intended role suggests internet access, but actual reachability is unclear.
  - You need to distinguish VM public exposure, LB VIP exposure, and NAT gateway public egress in Cloud.ru Evolution.
---

# Purpose

This skill is for diagnosing Cloud.ru Evolution connectivity when the user expects public access through a load balancer but the contour may actually be internal-only.

# Core rules

1. Separate admin access from service exposure.
   - If the user says `SSH не будет`, do not keep reasoning about direct host login.
   - Treat the task as a service-publication path: public IP -> LB -> listener -> backend target group -> backend VM port.

2. Verify where the public IP actually lands.
   - Do not trust names like `external`, `public`, or `web`.
   - Confirm whether the public IP is attached to:
     - a VM/direct interface;
     - a load balancer;
     - a NAT gateway.
   - A public IP on a NAT gateway gives egress, not inbound service access.

3. Inspect the LB reserve/VIP interfaces explicitly, but do not stop there.
   - In Cloud.ru Evolution, LB interfaces may appear in the interface list as `lbaas-reserve-*` with `type=vip`.
   - Those records are useful for mapping the NLB id and internal return addresses.
   - But they are not sufficient to prove whether the LB has a public frontend.
   - A public LB can still show only private `lbaas-reserve-*` interfaces in Compute while its real public IP is exposed only through the NLB service object.

4. When Compute/VPC reads are ambiguous, query the NLB service object directly.
   - Prefer the Terraform provider data sources for read-only NLB inspection when raw REST paths are unclear:
     - `cloudru_evolution_nlb_network_load_balancer_collection`
     - `cloudru_evolution_nlb_target_group_collection`
   - If the provider registry host is not directly discoverable by Terraform, use a local filesystem mirror with the provider binary from the Cloud.ru GitHub release and initialize Terraform against that mirror.
   - Read these fields from the NLB object first:
     - `external_address.ipv4`
     - `internal_address.ipv4`
     - `status`
     - `rules[].listeners[].port`
     - `rules[].listeners[].target_port`
     - `rules[].health_check`
     - `rules[].target_group_id`

5. Inspect backend VMs as backend nodes, not as public entry points.
   - Confirm private IPs, subnet, security groups, and intended service port.
   - If backend VMs have `floating_ip=null`, that is normal for a private-behind-LB contour.

# Minimal diagnostic sequence

1. Authenticate to Cloud.ru IAM.
2. List VMs and identify backend nodes.
3. List interfaces for the project.
4. List floating/public IPs for the project.
5. Match public IP ownership if it is visible in Compute, but expect false negatives there.
   - VM and NAT-gateway public IPs can be visible through Compute reads.
   - NLB public IPs may be absent from `floating-ips` and interface reads even when the LB is genuinely internet-facing.
   - Therefore a missing LB public IP in Compute is only an intermediate observation, not a final conclusion.

6. If the LB object shows a public IP, perform an external probe before declaring failure.
   - Test the exact listener ports on the public IP.
   - For HTTP listeners, issue several requests and inspect whether responses alternate across backends.
   - If the public probe returns `200` from both backend pages, the LB path is working and the issue is likely a wrong expectation about protocol or port, not an LB outage.

7. For internal-only LBs, verify the data path from an internal admin VM to the LB VIP.
   - Use the internal VIP from `internal_address.ipv4`.
   - Probe the exact configured listener port first, usually `http://<vip>:80/` when the rule is `80 -> 80`.
   - If direct pings to backend VMs succeed or partially succeed but `curl` to the LB VIP returns `Recv failure: Connection reset by peer`, do not stop at SG analysis.
   - Compare target-group members against the current VM inventory by VM ID and interface ID.
   - Recreated VMs can keep the same role/name while the LB target group still points at stale member objects.

# What to conclude from the confirmed pattern

If you observe an internal LB with these facts:
- `internal_address.ipv4` is populated;
- `status` is running;
- the listener is `80 -> 80`;
- SG rules allow admin/internal to app/internal traffic;
- direct probes to backend VM IPs are at least partially reachable;
- but `curl http://<internal-vip>/` returns `Recv failure: Connection reset by peer`;
- and the LB target-group member IDs do not match the IDs/interface IDs of the currently running backend VMs;

then the likely root cause is stale target-group membership after VM recreation or replacement.
The fix is to update the target group to the current backend VM/interface objects, not to keep debugging generic network reachability.

If you observe all of the following from the NLB object and a live probe:
- `external_address.ipv4` is populated;
- `status` is running;
- listener `80 -> 80` exists;
- target group contains the expected backend VMs;
- repeated external HTTP requests return `200` and hit both backends;
- `443` and other unconfigured ports refuse connections;

then the formal conclusion is:
- the LB is healthy and internet-facing for the configured listener;
- the backend path is working;
- the real issue is expectation mismatch: the user is probing the wrong protocol/port or expecting host-level access through the LB IP.

If instead Compute shows only private `lbaas-reserve-*` VIPs and a NAT gateway public IP, do not stop there. Query the NLB object before concluding the LB is internal-only.

# Pitfalls

- Pitfall: concluding `LB is internal-only` from Compute interface data alone.
  Fix: treat `lbaas-reserve-*` plus `floating_ip=null` as a clue, not a verdict; read the NLB service object and check `external_address.ipv4` before finalizing.

- Pitfall: spending time on backend VM or security-group hypotheses before checking whether the public IP already serves the configured listener.
  Fix: after confirming the NLB object, probe the public IP on the listener port and verify a real response path through both backends.

- Pitfall: trusting LB target groups by VM names only after the user recreated or reattached machines.
  Fix: compare target-group membership against the current VM inventory by VM ID and interface ID. If the names look right but the IDs differ, treat the TG as stale and refresh its members.

- Pitfall: reading `connection reset by peer` from an internal LB VIP as generic network breakage.
  Fix: first confirm the listener port/protocol, then check whether the LB is pointing at stale backend members. A running LB with permissive SGs can still reset connections when the target group no longer matches the current backend VM objects.

# Reporting pattern

Lead with one of these conclusions:
- `У балансировщика нет публичного attachment; он внутренний.`
- `Публичный IP принадлежит NAT gateway, а не load balancer.`
- `Backend VM нормальные, но internet-facing точки входа у LB сейчас нет.`

Then add only the minimal supporting facts:
- backend VM private IPs;
- LB VIP private IPs;
- public IP owner.

# References

- `references/internal-vs-public-probe.md` — baseline internal-vs-public LB triage.
- `references/terraform-nlb-live-probe.md` — provider-mirror + Terraform data-source path for reading real NLB public IP, listeners, and target groups when Compute endpoints are misleading.
- `references/stale-target-group-members.md` — how to detect stale target-group membership after VM recreation by comparing TG member IDs/interface IDs with current compute VM objects.
