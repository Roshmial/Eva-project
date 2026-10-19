# Cloud.ru Evolution: VPC and VM create notes from live session

## Confirmed endpoint split

- Compute base URL: `https://compute.api.cloud.ru`
- VPC base URL: `https://vpc.api.cloud.ru`
- Compute uses paths like `/api/v1/vms`, `/api/v1/subnets`, `/api/v1/security-groups` with snake_case query params such as `project_id`.
- VPC uses paths like `/v1/vpcs` with camelCase query params such as `projectId`.

Live-confirmed example:
- `GET https://vpc.api.cloud.ru/v1/vpcs?projectId=<PROJECT_UUID>`

## Live network discovery pattern

1. List VPCs through VPC API.
2. List subnets through Compute API.
3. Cross-check VPC id, subnet name, AZ, and CIDR before any VM create.

Useful live reads:
- `GET https://compute.api.cloud.ru/api/v1/subnets?project_id=<PROJECT_UUID>`
- `GET https://compute.api.cloud.ru/api/v1/security-groups?project_id=<PROJECT_UUID>`
- `GET https://compute.api.cloud.ru/api/v1/availability-zones?project_id=<PROJECT_UUID>`

## Live schema notes that mattered

### VM create

- VM create request accepts `availability_zone_name` for VM placement.
- VM create can use `subnets` or `interfaces` depending on versioned schema; the v1.1 create shape exposes `interfaces` explicitly.
- Public external address is requested at interface/subnet attachment time, not as a separate post-step by default.
- For a public-only VM with no private subnet attachment, the confirmed working shape was:
  - `POST https://compute.api.cloud.ru/api/v1.1/vms`
  - `interfaces: [{"type":"direct_ip","new_external_ip": true, ...}]`
  - root disk in `disks` as a new `40 GB SSD`
  - login/password/public key via `image_metadata`

Live validation pitfall:
- using `type: direct_ip` without `new_external_ip: true` or an existing attached public IP reference returned:
  - `422 Direct IP is allowed either with new_external_ip or attach_external_ip_id/attach_external_ip_name`

### Extra disk create and attach

Confirmed working flow:
1. `POST https://compute.api.cloud.ru/api/v1/disks` with:
   - `project_id`
   - `availability_zone_name` or id
   - `name`
   - `size: 50`
   - `disk_type_name: SSD`
2. Poll disk detail until the disk becomes attachable.
3. `POST https://compute.api.cloud.ru/api/v1/disks/{disk_id}/attach` with:
   - `{"vm_id":"..."}`
4. Verify in VM detail that the disk appears under `disks` with `primary: false` and `state: in_use`.

Practical note:
- live disk state was observed as `available` before attach and `in_use` after attach, even though an earlier wait loop incorrectly looked for `created`.

### Subnet create

Observed mismatch versus expectation:
- Subnet create required `availability_zone_id`.
- Passing `availability_zone_name` to subnet create returned validation error.

Live error:
- `422 missing body.availability_zone_id`
- `422 extra_forbidden body.availability_zone_name`

## Important pitfall from this project

The user wanted:
- VPC: `Default`
- subnet name: `Default_ru.AZ-1`
- CIDR: `10.0.0.0/24`

But the project already had in the same `Default` VPC:
- `Default_ru.AZ-2`
- `10.0.0.0/24`

Trying to create `Default_ru.AZ-1` with the same CIDR in that VPC returned:
- `409 subnet_already_exists_in_vpc`

Operational lesson:
- Do not assume the default VPC contains one default subnet per AZ.
- Do not assume the same CIDR can be reused per AZ inside one VPC.
- Verify actual subnet inventory before promising an exact AZ + subnet-name + CIDR combination.

## What to tell the user when this happens

Be explicit that the blocker is not generic API failure.
State the exact constraint:
- the requested VPC exists;
- the requested subnet name does not;
- the requested CIDR is already occupied in that VPC;
- the exact requested contour therefore cannot be created without changing one of: VPC, subnet CIDR, or AZ/subnet requirement.
