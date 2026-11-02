---
name: remote-network-diagnostics
description: Use when diagnosing home-network failures remotely.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [network, remote, tailscale, streaming, diagnostics]
    related_skills: [server-security-hardening, systematic-debugging, windows-maintenance]
---

# Remote Network Diagnostics

## When to Use

Load this skill when a website, streaming service, smart device, or application fails only through a home router; when the user asks for remote diagnosis through Tailscale or a reverse tunnel; or when router, ISP, DNS, IPv6, MTU, CDN, and endpoint causes must be separated.

## Purpose

Diagnose failures that occur only behind a home router without opening an unnecessary public management endpoint. Separate router/ISP transport, endpoint-device behavior, application/account state, and service-specific CDN/DRM paths before changing configuration.

## Procedure

### 1. Lock the diagnostic scope and failing path

First establish whether the user wants a baseline audit of the LAN/router or only a service-specific workaround. If the user resets the scope to “diagnose the network and router,” stop steering toward application DNS overrides, account/region workarounds, or VPN policy changes; complete the baseline first and keep service remediation as a separate conclusion.

Ask only for details that change the probes:

- exact playback device and application/browser;
- whether the same title works through a mobile hotspot;
- whether all content or one title fails;
- whether VPN is on the router, only on the diagnostic computer, or both;
- whether custom DNS, ad blocking, parental controls, IPv6, or policy routing is enabled.

A hotspot comparison is a discriminator only after egress provenance is explicit: failure without VPN may merely confirm a region requirement, while success through the same VPN on another device isolates the appliance/router path.

Build the physical and logical topology before attributing an appliance IP, MAC address, or radio metric. Inventory repeaters, wireless bridges, mesh nodes, powerline adapters, and downstream access points. A repeater can proxy several client IPs behind one locally administered MAC, so the main router may show the bridge MAC for the appliance while a client on the downstream segment sees the appliance's real OUI. Treat an endpoint behind a repeater as a two-hop path and audit both radios.

### 2. Reuse a private overlay before creating a reverse tunnel

Check whether the diagnostic host and home computer are already peers in Tailscale or another authenticated overlay. Prefer that path over a public reverse SSH relay, especially behind CGNAT.

For a userspace Tailscale daemon, address its real control socket explicitly:

```bash
tailscale --socket=/path/to/tailscaled.sock status
tailscale --socket=/path/to/tailscaled.sock ping <home-peer>
```

Do not infer shell access from an overlay ping. Ping proves the peer path; a remote shell still requires a listening, authenticated service on the target.

### 3. Test through the actual home egress before requesting shell access

If the home peer advertises an exit node and the diagnostic daemon is already using it, verify `ExitNodeStatus`, then compare public IPs and service endpoints through the daemon's SOCKS listener:

```bash
curl -fsS https://api.ipify.org
curl -fsS --socks5-hostname 127.0.0.1:PORT https://api.ipify.org
curl -sS -o /dev/null --socks5-hostname 127.0.0.1:PORT \
  --connect-timeout 8 --max-time 20 \
  -w 'code=%{http_code} tls=%{time_appconnect} total=%{time_total}\n' \
  https://service.example/
```

Prove which egress was measured before attributing it to the router. A home peer acting as an exit node can itself run a local VPN, so its SOCKS/exit-node public IP may be the computer's VPN egress rather than the router's WAN egress. Compare the IP from the peer, from a router shell, and—when safe—from a LAN host with its local VPN disabled or bypassed. Use remote DNS (`--socks5-hostname`) for the path under test, otherwise the diagnostic host's resolver can mask DNS behavior.

Do not clear a Windows VPN merely because the ordinary default route still points to the home router or no tunnel adapter is visible. WFP/DCO-based clients can intercept selected traffic without replacing `0.0.0.0/0`. For every throughput control, record the test tool's chosen internal IP, public IP/ASN, server geography and physical adapter MAC; treat a source IP outside the LAN or an unexpected foreign egress as a VPN-path measurement even if the tool reports `isVpn=false`. Stop the complete VPN application/process/service set in a reversible A/B, verify direct egress provenance, then restore the exact prior service state; a speed change without provenance is not evidence about the router.

A `403` or `404` from an API/CDN root can still prove DNS, TCP and TLS reachability; classify application authorization separately from transport.

### 4. Probe the service by layer

Use this order so a healthy landing page does not prematurely clear the network:

1. DNS A and AAAA resolution.
2. IPv4 and IPv6 connectivity separately.
3. TCP 443 and TLS handshake.
4. Main web/API hosts.
5. Media CDN and edge hosts discovered from the live application page or official network requirements.
6. MTU/fragmentation and large-transfer behavior.
7. QUIC/HTTP3 versus TCP fallback.
8. Device time, certificate trust, application cache, DRM/account authorization, region and concurrent-stream limits.

Successful access to the marketing page does not prove playback: manifests, license servers, media segments and DRM may use different hosts and protocols.

From a LAN host, query the router DNS explicitly and compare it with public resolvers. Do not trust a successful default lookup: Windows may silently use DNS from a VPN or another active adapter. Conversely, do not call repeated router-DNS timeouts a router fault while the probing host has an active VPN: DNS-leak protection can block direct UDP/53 to the LAN. Validate the router resolver locally on the router, inspect its listening socket/upstream resolvers, and repeat from a non-VPN LAN path before proposing an appliance DNS override.

For a streaming failure, run a same-device path matrix before changing more radio settings: home Wi-Fi without VPN, cellular without VPN, home Wi-Fi with VPN, and home Wi-Fi without VPN but with only the resolver changed. If cellular and VPN work, the account/device and general service are probably healthy. If changing only DNS on the same home path restores playback, classify the fault as resolver-specific CDN selection, stale resolver cache, or resolver reachability—not as Wi-Fi interference or a generally broken ISP route. Record and test the configured resolver addresses literally before calling one invalid; similar addresses such as `8.8.4.4` and `8.8.8.4` must never be normalized from memory. A resolver can answer ordinary lookups yet still steer a streaming client to a problematic CDN edge.

After changing DNS on the router, return the test client to automatic DNS and reproduce the same title on the original appliance. Restart the appliance first to clear cached DNS/session state. If another device on the same Wi-Fi and Apple ID plays the title while the appliance reports “no access” or “unavailable,” move to account, region, entitlement, and app-session checks before resetting the device or changing the network again. Treat a reduced catalog, obsolete application links, and a “latest available” OS that is older than the current supported branch as device-lifecycle evidence: “fully updated for this model” does not mean “currently supported platform.”

Do not infer Wi-Fi loss from ICMP alone on a smart appliance; power saving and ICMP rate limiting can produce dramatic ping loss. Compare repeated TCP connection success and latency to a known-open appliance port before diagnosing the radio path. For router and repeater baselines, send ICMP no faster than once per second; faster probes can trigger control-plane rate limiting and manufacture apparent loss.

When performance is the complaint, split the work into independent tracks and finish the main-router baseline before tuning the repeater or channel width. Change exactly one factor per A/B pass: local VPN on versus off, repeater versus direct AP, 80 versus 160 MHz, or one versus several TCP streams. Before every pass, record and validate the actual BSSID, PHY rates, RSSI, channel, gateway, and default route; abort a “direct AP” test if the client roamed to the repeater. Treat a NIC label such as `160MHz` as hardware capability, never proof of the negotiated width.

Use the same regional endpoint within each A/B pair, but require at least two independent regional servers before calling a client or router capped: public download and iPerf endpoints can vary dramatically by route and load. Record gateway latency under load and adapter error counters alongside throughput. A router-built-in speed test, a download started on the router shell, or a wired LAN client is the decisive WAN control because it excludes client Wi-Fi and the repeater. Choose endpoints reachable in the user's actual region; do not use a blocked CDN or service as a neutral benchmark.

Keep a per-run evidence ledger with BSSID/path, negotiated width, VPN egress provenance, endpoint, protocol/tool, stream count, throughput, loss/retransmits and timing. Never infer the root cause of an intermittent slowdown from temporal recovery after a service restart, VPN reset, radio restart or server change: a later full-rate run proves available capacity, not what caused earlier clean-path low runs. Before closing the diagnosis, reconcile every counterexample that used the same direct path without the proposed cause; if direct no-VPN client tests stayed slow while router-originated tests were fast, label the client-versus-router gap open rather than blaming VPN or the remote server. Likewise, do not turn two successful local-server speed tests into a claim that every route or single transfer can consume the tariff; separate last-mile capacity from destination/path performance.

For this user's network, preserve the legacy-compatible `Cathome` 2.4 GHz SSID and settings because smart-home devices depend on them. If Wi-Fi 6 is tested, enable `802.11ax` only on `Cathome_5G`, leave 2.4 GHz unchanged, state the temporary 5 GHz interruption, and verify both direct clients and the Keenetic backhaul after the radio restart.

Resolve the actual home egress geography/ASN and measure path MTU when a router VPN is present. A data-center/VPN egress or reduced PMTU can explain playback/DRM failures even when landing pages and API roots are reachable.

Reusable Windows commands and interpretation rules are in `references/windows-home-network-probes.md`.

### 5. Open a temporary shell only when endpoint-local evidence is needed

Prefer an existing authenticated remote-management service. Start with a local read-only collector when it can answer the diagnostic question; do not install a Windows optional feature merely to obtain interactive access unless the next probes genuinely require a shell.

Before enabling temporary Windows SSH, query the exact `OpenSSH.Server` capability instead of enumerating every capability. Record whether it was already installed before changing anything. If installation is required, tell the user before starting that DISM/CBS may need Windows Update and may run for several minutes. After `Add-WindowsCapability`, query `Get-WindowsCapability` again and decide from its actual `State`; do not read `State` from the add operation's return object, which may expose only fields such as `Online` and `RestartNeeded`. As soon as the re-query confirms installation, persist the prior-state/installed-by-diagnostics marker before configuring keys or firewall rules; otherwise a later script failure can leave an installed service that cleanup mistakenly treats as pre-existing. Show named stages and elapsed progress; never hide a long servicing call behind a generic `Running` indicator or `Out-Null`. Distinguish active servicing from a stall by comparing `TiWorker` CPU over time and reading both DISM and CBS tails. For Windows PowerShell 5.1 scripts delivered as files, keep the executable source ASCII-only or write UTF-8 with BOM; UTF-8 without BOM can turn Cyrillic string literals into parser errors. In ASCII collectors, never hard-code a localized adapter alias such as the Russian display name for Wi-Fi: discover the adapter from `InterfaceDescription`, GUID, or another locale-neutral property and pass its live `Name`. When replacing a user-downloaded script after a correction, publish a versioned filename and a visible version marker; chat clients and Downloads folders can retain the stale same-named attachment.

If temporary SSH is necessary:

- use a one-time public key, never a chat-supplied password;
- restrict the firewall to the exact overlay source and target addresses;
- preserve existing authorized keys and firewall policy;
- avoid exposing port 22 through the router;
- verify the service is reachable before claiming access;
- record a cleanup path before connecting.

With a userspace Tailscale daemon, use its byte-stream command as the SSH proxy when available:

```bash
ssh -o 'ProxyCommand=tailscale --socket=/path/to/tailscaled.sock nc %h %p' user@peer
```

For a LAN router behind that Windows peer, enable router SSH for LAN only, install a one-time public key without requesting the admin password, and create a second local forward through the authenticated Windows SSH session. Verify the router login before starting the audit; lowercase/normalized router usernames can differ from the UI display value.

Do not describe a generated enablement script as proven until the target actually runs it and the authenticated session succeeds. Before building a Windows `portproxy`, verify tailnet ACLs, `shields-up`, the listener from the target itself, and end-to-end reachability from the diagnostic peer. Prefer Tailscale Serve for a private tailnet-only TCP publication when ordinary Windows port forwarding cannot receive traffic; never substitute Funnel or WAN management exposure. Verify the published service with the real protocol client (`ssh -vv` with the intended ProxyCommand and key), not only a handcrafted banner or empty netcat probe: a half-closed byte-stream test can return no payload even when the SSH path works. Before asking the user to install or reuse a router public key, verify that the matching private key still exists and that its fingerprint matches; ephemeral scratch keys may have been pruned, so generate a fresh one-time pair instead of discovering the mismatch after access is opened. Cap access bootstrap at one corrective attempt: if the private channel still is not verified, stop stacking portproxy, firewall, Shields Up and Serve instructions unless the user explicitly chooses continued access work; fall back to a local collector or the router's built-in test. Use `references/asus-router-readonly-audit.md` for the validated ASUSWRT access chain and baseline audit. When an extender or wireless bridge is present, use `references/repeater-topology-and-keenetic-rci.md` to identify the real management address, separate proxy MACs from endpoint MACs, and collect authenticated Keenetic state without exposing its password.

A router reboot or radio restart can invalidate the nested local forward even after the LAN router is healthy again. Recreate the forward and re-authenticate before treating `connection refused` on the loopback port as a router failure.

### 6. Close the access and verify the fix

After diagnosis, close nested access from inside out so a partial cleanup remains repairable. Preserve services and policy that predated the session: remove only the temporary key/forward/rule unless the diagnostic work itself enabled the underlying service. Never claim persistent key removal from a successful command alone; read back the persistent store, clear the runtime file, and prove a fresh key login fails. If firmware protects the persistent key store, report the remaining authenticated-UI cleanup explicitly rather than attempting raw NVRAM/flash edits.

- remove the router key, disable its temporary management service, and verify the router port is closed from the LAN computer;
- only then remove the LAN computer's one-time key and firewall rule, and stop, disable, or uninstall its temporary service according to the recorded prior state;
- perform and verify service uninstall/rollback before restoring Tailscale `shields-up` or removing the last overlay rule; closing the outer control path first prevents read-back and can strand a temporary service;
- verify the final capability/service state and the outer remote port closure before deleting local keys and forwards;
- retest playback on the original device and network;
- state which layer failed and which exact change fixed it.

A reachable endpoint is intermediate evidence. Completion requires either reproduced playback or a clearly identified external blocker.

## User-facing delivery

Lead with what was already verified through the user's real home egress, then request the smallest next action. Distinguish confirmed transport facts from hypotheses about DNS, IPv6, MTU, QUIC, CDN, DRM, region, and account state. Keep temporary-access instructions brief and state how access will be removed.

Before recommending replacement network or media hardware, map every claimed benefit to the known topology and the user's existing devices. Do not sell faster gaming hardware when gaming is already covered elsewhere, or Wi-Fi 7 behind a Wi-Fi 5/6 bottleneck; compare only benefits that survive the actual path, such as OS-support horizon, application compatibility, codecs, Ethernet, or smart-home protocols.

Do not frame a domestic resolver as an inherent privacy loss while treating Google, Cloudflare, Amazon, or another foreign provider as privacy-preserving by default. All resolver choices expose metadata under some trust model; compare documented logging, encryption, interception risk, jurisdiction, reachability, and the user's threat model symmetrically. Distinguish DNS metadata (domains and timing) from application/search content visible to the service itself.