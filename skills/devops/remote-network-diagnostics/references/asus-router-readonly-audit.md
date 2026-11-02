# ASUSWRT router access and read-only baseline audit

Use this recipe when an ASUS router behind CGNAT must be inspected through an already authenticated LAN computer. Keep diagnosis and remediation separate; firmware, radio, VPN, DNS, and reboot changes need explicit approval.

## Access chain

1. Reach the LAN computer through the existing private overlay.
2. Enable Windows OpenSSH only if an interactive shell is genuinely required; use a one-time key and an exact overlay firewall scope.
3. In ASUSWRT, enable SSH as **LAN only**, keep WAN SSH disabled, and prefer public-key authentication. If the UI has no key field, let the user enter the router password locally and append the one-time public key; never request the password in chat.
4. Forward a local port through the Windows peer:

```bash
ssh -N \
  -o 'ProxyCommand=tailscale --socket=/path/tailscaled.sock nc %h %p' \
  -L 127.0.0.1:12222:192.168.50.1:22 windows-user@tailscale-peer
ssh -p 12222 -i /path/router-key router-user@127.0.0.1
```

Some ASUS/Dropbear builds normalize the login name to lowercase or need legacy RSA negotiation. Try the normalized username with batch mode before concluding that the key was rejected; enable `ssh-rsa` algorithms only for the loopback-forwarded legacy endpoint when required.

## Baseline order

### Identity and health

```sh
nvram get productid
nvram get firmver; nvram get buildno; nvram get extendno
uptime
cat /proc/loadavg
free
df -h
cat /proc/sys/net/netfilter/nf_conntrack_count
cat /proc/sys/net/netfilter/nf_conntrack_max
```

On stock ASUSWRT, `/dev/root` at 100% is normally the immutable firmware image, not a full writable disk. Judge writable capacity from `/jffs` and `/tmp`.

### Prove router WAN egress, not computer VPN egress

```sh
ip -4 addr show
ip -4 route show
wget -qO- -T 10 https://api.ipify.org
ping -c 30 -W 1 <wan-gateway>
ping -c 30 -W 1 1.1.1.1
```

Measure base MTU from the router. A reduced MTU observed on a Windows host with a local VPN describes that VPN path, not necessarily the router WAN.

### WAN link, QoS and router-originated throughput

Before blaming Wi-Fi or the ISP, confirm the physical WAN link and shaping state with targeted reads:

```sh
wan_if="$(nvram get wan0_ifname)"
cat "/sys/class/net/$wan_if/speed"
cat "/sys/class/net/$wan_if/duplex"
cat "/sys/class/net/$wan_if/carrier"
for k in qos_enable qos_type qos_ibw qos_obw; do printf '%s=' "$k"; nvram get "$k"; done
for x in rx_packets tx_packets rx_errors tx_errors rx_dropped tx_dropped; do
  printf '%s=' "$x"; cat "/sys/class/net/$wan_if/statistics/$x"
done
```

Use the stock router speed test when it can retrieve its configuration:

```sh
/usr/sbin/ookla -L -f json-pretty
/usr/sbin/ookla -f json-pretty --progress=no
```

If the bundled Ookla client cannot retrieve configuration because its control/CDN path is unavailable in the region, do not call that a WAN failure. Run `curl` directly on the router against the same reachable regional large-file endpoint used by the LAN host. Measure both one transfer and several concurrent transfers to separate a single-flow route limit from total WAN capacity:

```sh
/usr/sbin/curl -4 -L -sS -o /dev/null --connect-timeout 10 --max-time 180 \
  -w 'http=%{http_code} total=%{time_total} bytes=%{size_download} speed_Bps=%{speed_download}\n' \
  '<regional-large-file-url>'

rm -f /tmp/wan-speed.*
cat /proc/uptime > /tmp/wan-speed.start
for i in 1 2 3 4; do
  /usr/sbin/curl -4 -L -sS -o /dev/null --connect-timeout 10 --max-time 180 \
    -w "stream=$i total=%{time_total} bytes=%{size_download} speed_Bps=%{speed_download}\n" \
    "<regional-large-file-url>?stream=$i" > "/tmp/wan-speed.$i" 2>&1 &
done
wait
cat /proc/uptime > /tmp/wan-speed.end
cat /tmp/wan-speed.[1-4]
```

Compute aggregate throughput from total bytes divided by wall-clock time, not by summing each stream's instantaneous speed. A router-originated result near tariff speed clears WAN, QoS and the ISP path for that interval; compare it with direct-AP and repeater client results to quantify each radio penalty.

Do not infer end-to-end health by combining two separate successes. Router-originated WAN throughput and client-to-router LAN throughput bypass forwarding/NAT in opposite directions; both can be healthy while LAN-to-WAN transit remains slow. Measure all three legs with the same stream count and interval:

1. router-originated download from the regional endpoint;
2. raw client-to-router LAN transfer;
3. client download through the router to the same regional endpoint.

When `socat` is already present, a temporary zero-data source gives a storage-free LAN control:

```sh
socat TCP-LISTEN:18089,bind=<router-lan-ip>,reuseaddr,fork \
  SYSTEM:'dd if=/dev/zero bs=1048576 count=128 2>/dev/null'
```

Have the client read a fixed byte count with one and several TCP connections, calculate aggregate bytes over wall-clock time, then kill `socat` and verify that the listener disappeared. Bind only to the LAN address and never leave the probe running after the measurement.

If raw LAN and router-originated WAN are both fast but client Internet remains slow, compare plain HTTP with HTTPS to the same host before blaming TLS inspection. Similar HTTP/HTTPS results rule out encryption handling as the primary limiter. Next verify forwarding acceleration itself: a loaded module or enabled NVRAM flag is only configuration evidence, not proof that the measured flow was offloaded. On MediaTek ASUSWRT, inspect the live table during the client transfer:

```sh
nvram get hwnat
lsmod | grep mtkhnat
cat /sys/kernel/debug/hnat/whnat_interface
cat /sys/kernel/debug/hnat/hnat_entry
```

Require the client's LAN address and test server tuple to appear as a `BIND` entry during the transfer. Sample for a bounded interval in the background when the entry is short-lived, and remove the monitor file afterward. If the flow binds yet throughput is low, continue with client TCP/filter-stack and alternative-endpoint controls; do not repeatedly toggle NAT or reboot the router without new evidence. If the flow never binds, audit incompatible features and vendor acceleration state before changing radio settings.

### DNS

Read only targeted non-secret keys and runtime resolver files:

```sh
for k in wan_dnsenable_x wan_dns1_x wan_dns2_x dhcp_dns1_x dhcp_dns2_x dnssec_enable dnspriv_enable; do
  printf '%s=' "$k"; nvram get "$k"
done
sed -n '1,80p' /tmp/resolv.conf
sed -n '1,80p' /tmp/resolv.dnsmasq
ps w | grep '[d]nsmasq'
netstat -lnup | grep ':53 '
nslookup service.example 127.0.0.1
nslookup service.example <router-lan-ip>
```

Do not infer router DNS failure only from a Windows VPN host; leak protection can block LAN DNS. Reconcile NVRAM configuration with runtime resolvers and test locally plus from a non-VPN LAN client.

### VPN provenance

A UI label or stale `vpnc_default_wan` value does not prove an active router VPN. Require all of:

- a live VPN process;
- a tunnel interface/address;
- policy rules or route table entries;
- router public IP matching the intended VPN geography.

Enumerate only NVRAM key names when discovering the schema. Never dump broad `nvram show` values: VPN usernames, passwords, private keys, and pre-shared keys can be present.

### Wi-Fi

Map the appliance MAC to the bridge port, then to the radio:

```sh
ip neigh show <appliance-ip>
brctl show
brctl showmacs br0 | grep -i '<mac>'
brctl showstp br0
iwconfig ra0
iwconfig rax0
iwpriv ra0 stat
iwpriv rax0 stat
ip -s link show ra0
ip -s link show rax0
```

Treat `iwpriv ... stat` as whole-radio counters, not per-client proof. High Tx failure/PER and Rx CRC rates support interference or excessive channel width; correlate them with repeated TCP connects to a known-open appliance port. Heavy ICMP loss with nearly complete TCP success is usually appliance ICMP throttling or sleep behavior.

Before interpreting a client MAC, inspect DHCP leases, network-map state, the bridge forwarding table, and a site survey. Several client IPs resolving to one locally administered MAC usually indicates a wireless bridge or repeater doing proxy ARP/MAC translation. A nearby BSSID that mirrors the home SSID and shares the hardware portion of the repeater's OUI is further topology evidence; do not mislabel the proxy MAC as the appliance.

DFS operation plus 160 MHz width is a compatibility/stability risk for streaming devices. Propose 80 MHz only after the baseline is recorded, but do not assume channel 36 or another generic non-DFS channel is automatically better. Run a site survey from the router radio: a strong neighbor anywhere inside an 80 MHz block can make a seemingly free primary channel worse than the current DFS block, and widening to 160 MHz can capture a strong neighbor outside the current clean 80 MHz block. Verify actual width from router channel specification/runtime state and negotiated PHY; a Windows adapter description containing `160MHz` states capability, not the active width.

On stock MediaTek ASUSWRT, distinguish configured capability from runtime width. `wl1_bw_160=1` can merely permit 160 MHz; it does not prove the client negotiated it. On TUF-AX4200-family firmware, observed values are `wl1_bw=3` for the 80 MHz baseline and `wl1_bw=5` for 160 MHz, but read current values first and verify the exact build at runtime rather than applying the mapping blindly. Confirm with all three surfaces:

```sh
for k in wl1_bw wl1_bw_160 wl1_channel wl1_11ax; do printf '%s=' "$k"; nvram get "$k"; done
iwconfig rax0
iwpriv rax0 stat | grep -E 'Tx success|Tx fail count|Rx success|Rx with CRC|Last TX Rate|Last RX Rate'
```

After `service restart_wireless`, allow for DFS CAC and rate adaptation: wait until the overlay host reconnects and negotiated rates stabilize before starting the fixed interval. Change one radio factor at a time, then repeat identical direct-AP LAN and multi-server WAN tests while recording BSSID, PHY, gateway latency under load, and fixed-interval radio deltas. Radio restart and firmware upgrade reset cumulative counters, so calculate interval ratios from deltas, not the printed lifetime PER: `delta_fail / (delta_success + delta_fail)` and `delta_crc / (delta_rx_success + delta_crc)`. Prefer the width with materially lower error ratios when 160 MHz adds only a small multistream gain, reduces single-stream throughput, or fails to improve direct regional WAN tests. Roll back to the recorded values and verify runtime BW after the comparison. Changing channel/width disconnects clients and requires approval.

When legacy smart-home devices occupy a dedicated 2.4 GHz SSID, do not disable Wi-Fi 6 globally. Preserve the 2.4 GHz compatibility profile and, with approval, enable `802.11ax` only on the 5 GHz radio. Record the exact per-band NVRAM values before committing, restart only wireless, wait for the overlay host and repeater to reconnect, then verify the runtime mode with `iwconfig` and repeat the same direct-AP throughput test. An improved advertised radio rate is intermediate evidence; only client throughput and backhaul recovery complete the change.

`iwpriv ... stat` can print WPS PIN material. Do not retain, quote, or expose that output beyond extracting aggregate radio counters. Check WPS state through targeted NVRAM keys and recommend disabling it when unused.

### Firmware and exposure

Compare the exact installed build against the official ASUS support page, not a generic model page or memory. Check targeted service keys for WAN administration, SSH scope, Telnet, firewall, WPS, UPnP, AiCloud, IPv6, DNSSEC, and encrypted DNS. Classify each as fact, risk, or trade-off; UPnP may be intentional for consoles.

Prefer the authenticated ASUS web updater. If a remote shell update is explicitly approved and the normal UI is unavailable, use the stock firmware's own validation and upgrade path rather than writing flash devices directly:

1. Save a binary NVRAM backup with `nvram save /tmp/nvram-backup.bin`, transfer it with mode `0600`, and remove the remote copy. Some stock Dropbear builds lack SFTP; stream the file with `ssh 'dd if=…' > local-file` and verify a nonzero size instead of weakening SSH.
2. Download the exact official model package, compare the ZIP SHA-256 with the value published on the support page, test the archive, and verify the extracted TRX hash before and after transfer.
3. Obtain the matching vendor RSA signature indicated by `live_update_rsa_ver`. ASUS live-update objects can have a `.zip` suffix while containing raw signature bytes; place the bytes at the path expected by the stock validator rather than trying to unzip them.
4. Run both `firmware_check <trx>` and `rsasign_check <trx>` and require `nvram get firmware_check` and `nvram get rsasign_check` to equal `1`. Stop if either check fails.
5. Inspect the installed `webs_upgrade.sh` and invoke the same `linux.trx`/`fwpath`/`restart_upgrade` sequence used by that exact firmware family. Never generalize a flash sequence across unrelated models.
6. Observe a real down/up cycle from an independent LAN host, recreate the nested SSH forward, then verify the exact build, WAN reachability, DNS, radio settings, repeater recovery, and application path. A reboot command or returning ping alone is not completion.

The router's live-update metadata can lag the support page. Treat its “no update” result as one source, not proof that the installed build is current.

## Closeout

Before changing anything, state the exact change set and disruption: Wi-Fi restart, router reboot, firmware risk, or VPN route change. After approval, record current values, apply the smallest coherent set, and retest WAN/DNS/radio/application behavior.

Close access from the router outward, but preserve services that predated the diagnostic session. If LAN-only SSH was already enabled, remove only the one-time key; disable SSH only when the session enabled it. Verify cleanup at three layers:

1. the persistent key store no longer contains the diagnostic key;
2. the runtime `authorized_keys` file no longer contains it;
3. a fresh login with the diagnostic private key returns `Permission denied (publickey)`.

Do not assume `nvram unset sshd_authkeys` or `nvram set sshd_authkeys=''` worked merely because it returned zero. Some stock ASUSWRT builds store `sshd_authkeys` as encrypted NVRAM: ordinary CLI writes can silently leave the decrypted value unchanged, and restarting SSH can regenerate the runtime file from that persistent value. Read the value back in sanitized form and compare its key fingerprint/comment; never print the full key unnecessarily.

When encrypted NVRAM blocks persistent CLI removal, do not improvise flash/NVRAM editing. Clear the runtime `authorized_keys`, prove the key is rejected, securely delete the matching private key, and require the user to clear the Authorized Keys field through the authenticated ASUS UI. Report that persistent UI cleanup remains pending until it is read back or a later reboot confirms the key does not regenerate.

After the router key is closed, remove Tailscale Serve/portproxy listeners and exact firewall rules on the LAN computer, restore `shields-up` to its prior state, and verify both the local listener list and an external connection attempt. Only then delete remaining local key material and declare the diagnostic channel closed.