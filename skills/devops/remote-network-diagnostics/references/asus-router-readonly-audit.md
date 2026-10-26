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

DFS operation plus 160 MHz width is a compatibility/stability risk for streaming devices. Propose 80 MHz only after the baseline is recorded, but do not assume channel 36 or another generic non-DFS channel is automatically better. Survey the local spectrum, change one radio factor at a time, then compare counter deltas over the same fixed interval. Radio restart and firmware upgrade reset cumulative counters, so calculate fresh Tx-success/Tx-fail and Rx-success/Rx-CRC deltas for 30–60 seconds; rollback or select the previously healthier channel when the interval worsens. Changing channel/width disconnects clients and requires approval.

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

Close access from the router outward. On stock ASUSWRT/Dropbear, persist `sshd_enable=0`, clear `sshd_authkeys`, commit NVRAM, remove the generated `authorized_keys`, then stop the active Dropbear process and verify port 22 is closed from the LAN computer. Do not use `service restart_sshd` as the cleanup action when disabling SSH: some builds regenerate the key and restore the enabled state during restart. Keep the Windows access alive until this verification passes; only then remove the Windows key/firewall rule and verify its SSH port is closed.