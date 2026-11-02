# Windows home-network probes

Use these probes from a Windows host on the same LAN as the failing appliance. Keep them read-only until one layer is isolated.

## Identify the real interface and DNS sources

```powershell
Get-NetIPConfiguration | Where-Object {$_.NetAdapter.Status -eq 'Up'} | ForEach-Object {
  [pscustomobject]@{
    Interface = $_.InterfaceAlias
    IPv4      = $_.IPv4Address.IPAddress -join ','
    Gateway   = $_.IPv4DefaultGateway.NextHop -join ','
    DNS       = $_.DNSServer.ServerAddresses -join ','
  }
}
Get-NetRoute -AddressFamily IPv4 | Where-Object DestinationPrefix -eq '0.0.0.0/0'
```

Inspect every active adapter. VPN adapters can supply DNS even without the preferred default route, masking a broken router resolver. Also treat the route table as insufficient proof that VPN is off: WFP/DCO clients can intercept selected applications while `0.0.0.0/0` still points to the home gateway and no tunnel adapter is visible.

For an internet-speed baseline, use a tool that reports path provenance as well as throughput. With official Ookla CLI JSON, retain `interface.internalIp`, `interface.externalIp`, physical MAC, ISP, server country/location, latency and packet loss. The `isVpn` flag is advisory: if `internalIp` is not the LAN address, the physical MAC is absent, or the public ASN/geography differs from a direct `api.ipify.org`/router check, classify the run as VPN-intercepted. Run at least two nearby regional servers after restoring direct egress; one foreign auto-selected server or one public iPerf endpoint is not a router baseline.

## Measure Wi-Fi performance from the LAN host

Do not diagnose Wi-Fi throughput from a remote download routed through a Tailscale exit node. That path carries the payload back through the home's upstream link and overlay, so it can measure home upload or relay overhead rather than local Wi-Fi download. Use it only as a reachability and rough egress check.

First confirm whether the probe host is actually on Wi-Fi:

```powershell
netsh wlan show interfaces
Get-NetAdapter | Where-Object Status -eq 'Up' |
  Select-Object Name,InterfaceDescription,LinkSpeed,MacAddress
```

Record SSID, BSSID, radio type, channel, receive/transmit rate and signal. If the host is on Ethernet, its internet test is a WAN baseline, not a Wi-Fi measurement. With a repeater or wireless bridge, the connected BSSID identifies only the client-to-node hop; audit the node's wireless backhaul separately.

Measure the local radio/LAN path before the internet path:

```powershell
$gw = (Get-NetRoute -AddressFamily IPv4 -DestinationPrefix '0.0.0.0/0' |
  Sort-Object RouteMetric | Select-Object -First 1).NextHop
ping.exe -n 100 $gw
```

Stable sub-10 ms gateway latency with negligible loss usually clears the client-to-access-point hop under light load. Repeat the ping while a large local or internet transfer runs; latency spikes and loss only under load point to airtime contention, weak signal, backhaul saturation or bufferbloat.

Then measure the internet path locally on Windows, not through the remote overlay. Choose a large-file endpoint that is reachable in the user's region and keep it identical across A/B passes:

```powershell
$url = '<regional-large-file-url>'
1..3 | ForEach-Object {
  curl.exe -L -o NUL -sS --connect-timeout 10 --max-time 180 `
    -w "run=$_ http=%{http_code} ttfb=%{time_starttransfer} total=%{time_total} bytes=%{size_download} speed_Bps=%{speed_download}`n" `
    $url
}
```

Compare at least three runs because Wi-Fi rate adaptation and shared airtime create variance. Repeat one versus four parallel transfers: if aggregate throughput rises substantially, a single TCP path or test server was limiting; if it remains capped, continue isolating Wi-Fi, repeater and WAN. When possible, repeat on Ethernet and on the main router versus the repeater: the resulting matrix separates WAN, client radio and wireless-backhaul bottlenecks.

For a stubborn throughput ceiling, build a three-leg matrix before changing more radio settings:

1. Router-originated WAN transfer: excludes client Wi-Fi and the LAN-to-WAN forwarding path.
2. LAN-only transfer from the router or another wired host to the client: excludes the ISP, DNS and NAT.
3. Client-to-WAN transfer through the router: exercises the full forwarding path.

If legs 1 and 2 are fast while leg 3 is slow, the radio and WAN are independently healthy; inspect client filters/TCP behavior and the router forwarding/offload path. Do not infer working hardware NAT merely because an HNAT module is loaded. Capture the acceleration table during the client transfer and require bound entries for the client's exact source address and test destination. If those flows are bound, stop blaming NAT configuration and use a reversible endpoint A/B test: record service/adapter state, stop only the suspected VPN/filter components, rerun the identical transfer, and restore the exact prior state in `finally`. Treat a loaded VPN driver or an RSC `WFPCompatibility` state as a hypothesis until that A/B changes throughput.

## Compare router DNS with public DNS

```powershell
foreach ($server in @('192.168.1.1','1.1.1.1','8.8.8.8')) {
  foreach ($name in @('service.example','media-edge.example')) {
    $sw=[Diagnostics.Stopwatch]::StartNew()
    try {
      $r=Resolve-DnsName $name -Server $server -Type A -DnsOnly -ErrorAction Stop
      $ok=$true; $ips=(@($r|Where-Object IPAddress).IPAddress)-join','
    } catch { $ok=$false; $ips=$_.Exception.Message }
    $sw.Stop()
    "server=$server name=$name ok=$ok ms=$($sw.ElapsedMilliseconds) ips=$ips"
  }
}
```

Repeat router queries rather than relying on one timeout. If the Windows host has an active VPN, treat router-DNS timeouts as ambiguous: leak protection may block LAN UDP/53 even when the router resolver is healthy. Validate with `nslookup` on the router itself, confirm `dnsmasq`/the resolver is listening on the LAN address, and repeat from a non-VPN LAN path before changing appliance DNS.

## Separate appliance ICMP behavior from real LAN loss

First identify a known-open local service port, then compare ping with repeated TCP connects:

```powershell
ping.exe -n 50 <appliance-ip>

$success=0; $fail=0; $times=New-Object System.Collections.Generic.List[long]
1..50 | ForEach-Object {
  $client=New-Object Net.Sockets.TcpClient
  $sw=[Diagnostics.Stopwatch]::StartNew()
  try {
    $task=$client.ConnectAsync('<appliance-ip>',<known-open-port>)
    if ($task.Wait(1000) -and $client.Connected) {
      $success++; $times.Add($sw.ElapsedMilliseconds)
    } else { $fail++ }
  } catch { $fail++ } finally { $sw.Stop(); $client.Dispose() }
  Start-Sleep -Milliseconds 100
}
"success=$success fail=$fail average_ms=$([math]::Round(($times|Measure-Object -Average).Average,1))"
```

Heavy ping loss with nearly complete TCP success points to ICMP throttling or sleep behavior, not equivalent application-packet loss. Prefer a real local application endpoint when available—for example, AirPlay `/info` on an Apple TV—and run several sequential requests. A first cold timeout followed by fast HTTP 200 responses can be device wake-up behavior; never classify the link from the first request alone.

## Measure path MTU conservatively

```powershell
foreach ($payload in @(1472,1464,1452,1440,1432,1424,1416,1408,1400)) {
  $null=ping.exe -n 2 -w 2000 -f -l $payload 1.1.1.1
  "payload=$payload success=$($LASTEXITCODE -eq 0)"
}
```

For IPv4 ICMP, approximate path MTU as the largest successful payload plus 28 bytes. A lower path MTU is evidence, not automatically the root cause; correlate it with VPN encapsulation, QUIC/media behavior, and TCP MSS handling.

## Preflight temporary Windows OpenSSH

```powershell
Get-WindowsCapability -Online -Name 'OpenSSH.Server~~~~0.0.1.0'
Get-Service sshd -ErrorAction SilentlyContinue
```

Prefer a local collector if OpenSSH is absent. If installation is justified, capture the initial state first, run `Add-WindowsCapability`, then re-query `Get-WindowsCapability` and require the returned capability's `State` to be `Installed`. The add operation's own result may not contain a `State` property, so testing `$result.State` can falsely report failure after a successful installation. Immediately after the successful re-query, write an installed-by-diagnostics marker or prior-state record; do not wait until later key/firewall setup succeeds. Cleanup must decide uninstall versus preserve from that recorded initial state, verify `OPENSSH_FINAL_STATE`, and only then restore Tailscale `shields-up`; reversing those last two steps locks out the verification channel. Keep the operation visible and diagnose long servicing with:

```powershell
Get-Process TiWorker,TrustedInstaller -ErrorAction SilentlyContinue |
  Select-Object Name,Id,CPU,StartTime
Get-Content C:\Windows\Logs\DISM\dism.log -Tail 30
Get-Content C:\Windows\Logs\CBS\CBS.log -Tail 40
```

A single CPU value proves only that work occurred; compare values over a fixed interval before calling the operation active or stalled.

## Run multiline probes reliably over Windows SSH

Do not rely on `powershell.exe -Command -` for a multiline script containing blocks and formatting pipelines; stdin execution can stop after an early statement while returning exit code 0. Copy the collector with `scp`, then execute it with `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <path>`. Require a terminal marker or expected section count so partial output cannot be mistaken for a complete probe.

Keep Windows PowerShell 5.1 collectors ASCII-only unless they are explicitly written with a BOM. Do not hard-code localized interface aliases inside an otherwise ASCII script; discover the target by `InterfaceDescription`, GUID, MAC address, or another stable locale-neutral property, then use the live adapter `Name`. Never name a function parameter or ordinary variable `$host`: PowerShell variable names are case-insensitive and `$Host` is a read-only automatic variable, so parameter binding fails before the probe starts. After fixing a delivered script, change the filename (for example, add `-v2`) and print the version at startup so a cached or duplicate file in Downloads cannot silently rerun the old code.