# Cloud.ru LB internal-vs-public probe

Live-confirmed project pattern:

- project_id: `6649fb7f-140c-401a-9420-16948b8aa5aa`
- backend VMs:
  - `vm-app-external1` -> `192.168.100.5`
  - `vm-app-external2` -> `192.168.100.6`
- backend VM interfaces:
  - subnet `subnet-app-external` / `192.168.100.0/24`
  - `floating_ip = null` on both VMs
- public IP inventory:
  - only public IP found: `176.123.167.100`
  - owner: NAT gateway `gateway-vpc-web`
- LB reserve interfaces:
  - multiple `lbaas-reserve-*` entries with descriptions like `{"nlb_id":"4c10e11d-79fb-46e5-8df5-2a18fdaf2689","type":"output"}`
  - all had private addresses in `192.168.100.0/24`
  - all had `type = vip`
  - all had `floating_ip = null`

Operational conclusion from this pattern:

- the LB named/treated as external was actually internal-only;
- internet ingress could not work because no public attachment existed on that LB;
- the public IP in the project belonged to NAT egress, not to LB ingress.

Useful API reads that exposed this fast:

- `GET https://compute.api.cloud.ru/api/v1/vms?project_id=<PROJECT_ID>`
- `GET https://compute.api.cloud.ru/api/v1/interfaces?project_id=<PROJECT_ID>`
- `GET https://compute.api.cloud.ru/api/v1/floating-ips?project_id=<PROJECT_ID>`
- `GET https://compute.api.cloud.ru/api/v1/security-groups?project_id=<PROJECT_ID>`

Reading rule:

- If the user says SSH is out of scope, stop reasoning about host login.
- First prove whether the LB is truly public or only private-with-NAT.
