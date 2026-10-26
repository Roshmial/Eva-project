# Repeater topology and Keenetic audit/tuning

Use this recipe when an endpoint sits behind a wireless extender or bridge, especially a Keenetic in Extender mode. Diagnose the main router, backhaul, extender, and endpoint as separate links; apply configuration or firmware changes only after a credential-free topology pass and an authenticated backup.

## 1. Establish the topology before tuning radios

From the main router, correlate:

```sh
ip neigh show
brctl showmacs br0
cat /var/lib/misc/dnsmasq.leases
# ASUS MediaTek examples
iwconfig rax0
iwpriv rax0 get_site_survey
iwpriv rax0 stat
```

Indicators of a repeater/bridge:

- several downstream IPs resolve to one locally administered MAC on the main router;
- DHCP identifies a separate management MAC and hostname for the extender;
- the site survey shows a strong BSSID rebroadcasting the household SSID;
- a directly attached LAN computer sees the endpoint's real vendor OUI while the main router sees the bridge/proxy MAC.

Do not assume a historical DHCP address is current. After a channel restart or reboot, read the live lease/network-map state again and probe the new management address.

## 2. Validate each hop with the right signal

For the main-router-to-repeater backhaul, record channel, width, RSSI/link rates, and whole-radio error-counter deltas over a fixed interval. For the repeater management path, require repeated ping or HTTP success. For the endpoint path, compare repeated TCP connects or a real local HTTP endpoint with ICMP; smart appliances commonly throttle ping.

A strong RSSI does not clear the backhaul when CRC or retry deltas remain high. Conversely, a high cumulative radio percentage immediately after changing channel is not comparable with a pre-restart lifetime percentage; use equal-duration deltas.

## 3. Discover Keenetic without credentials

A Keenetic web response can identify its operating mode through headers such as `Ndm-Sysmode: extender`. Confirm the management IP from the main router's current DHCP lease and vendor MAC, then check ports 80/443 and latency. This establishes reachability but does not expose firmware, interfaces, associations, or configuration.

## 4. Collect authenticated state without sharing the password

Never request the Keenetic password in chat or place it in a command line. Run a local collector on a LAN computer that reads the exact Keenetic login with `Read-Host` and the password with `Read-Host -AsSecureString`, authenticates in memory, writes only selected read-only JSON, and returns the artifact path. Prefer explicit login input over `Get-Credential`: Windows credential UI can blur Keenetic and Windows identities.

Keenetic LAN RCI uses challenge-response:

```text
GET /auth -> X-NDM-Realm, X-NDM-Challenge, session cookie
md5 = MD5(login + ":" + realm + ":" + password) as lowercase hex
key = SHA256(challenge + md5) as lowercase hex
POST /auth {"login":"…","password":"<key>"}
```

Keep the cookie in one web session, zero/free the temporary password buffer, and never serialize credentials or the derived key. In Windows PowerShell 5, send the authentication JSON as explicit UTF-8 bytes; otherwise non-ASCII or implicit body encoding can yield a misleading 401. On 401, reacquire a fresh challenge/session and retry the local credential prompt—do not open WAN management, change service ports, or weaken access controls. Collect only the endpoints required for diagnosis:

```text
/rci/show/version
/rci/show/system
/rci/show/interface
/rci/show/associations
/rci/show/internet/status
/rci/show/ip/route
/rci/show/last-change
/rci/show/dns-proxy
```

Avoid `/rci/`, running/startup configuration, user branches, and broad configuration exports unless the task explicitly requires them; they can contain secrets. Treat HTTP 200 bodies containing `status[].status == "error"` as failures.

## 5. Tune and verify in dependency order

1. Inventory clients on both extender bands before changing radios. `show/associations` identifies the actual access-point interface: a 5 GHz backhaul does not imply that the endpoint itself uses 5 GHz. Do not prescribe 5 GHz for the endpoint by default: on a dual-band extender, a strong 2.4 GHz client link plus 5 GHz backhaul can avoid same-radio repeat airtime and outperform a 5 GHz client sharing the backhaul radio. Compare the real application on both bands and keep the band that actually works better.
2. Preserve 2.4 GHz SSID, password and WPA mode when smart-home devices depend on it. Do not disable or rename that band as an optimization shortcut.
3. Stabilize the main router first, then confirm the extender reconnects on its current management IP and the endpoint returns.
4. On congested 2.4 GHz, prefer 20 MHz and non-overlapping channels 1, 6 or 11. When the extender uses an independent 2.4 GHz radio, place it on a different non-overlapping channel from the main router; warn that clients will briefly reconnect.
5. Audit extender firmware, backhaul association, channel/width, DNS and routing state before extender-specific changes.
6. Retest the endpoint's real application path and compare fixed-interval radio deltas on both hops.

For authenticated changes, first download `/ci/startup-config.txt` to the user's LAN computer and verify the file is non-empty. Use `POST /rci/parse` with a JSON string for exact CLI commands, save the configuration, and read back `/rci/show/interface`; never infer success from HTTP 200 alone.

For a controlled KeeneticOS Main-channel update:

1. Verify the exact model/hardware ID, extender mode, current version and official target release.
2. Start and poll `POST /rci/components/list` until the background operation returns a final target; refuse an unexpected channel/version.
3. Start `POST /rci/components/commit`, expect the management session to drop, and observe an actual down/up cycle.
4. Reauthenticate after reboot and verify firmware version, radio settings, gateway, DNS and `show/last-change` unsaved state.
5. Keep credentials only as a `SecureString` in the local process; never persist or return them in the result artifact.

Do not call a streaming problem fixed merely because the extender is reachable. Separate local path health from router egress geography, VPN policy, CDN/DRM authorization, and account region.