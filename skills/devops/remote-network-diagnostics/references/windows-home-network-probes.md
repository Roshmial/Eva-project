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

Inspect every active adapter. VPN adapters can supply DNS even without the preferred default route, masking a broken router resolver.

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

Prefer a local collector if OpenSSH is absent. If installation is justified, keep the operation visible and diagnose long servicing with:

```powershell
Get-Process TiWorker,TrustedInstaller -ErrorAction SilentlyContinue |
  Select-Object Name,Id,CPU,StartTime
Get-Content C:\Windows\Logs\DISM\dism.log -Tail 30
Get-Content C:\Windows\Logs\CBS\CBS.log -Tail 40
```

A single CPU value proves only that work occurred; compare values over a fixed interval before calling the operation active or stalled.

## Run multiline probes reliably over Windows SSH

Do not rely on `powershell.exe -Command -` for a multiline script containing blocks and formatting pipelines; stdin execution can stop after an early statement while returning exit code 0. Copy the collector with `scp`, then execute it with `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <path>`. Require a terminal marker or expected section count so partial output cannot be mistaken for a complete probe.