# Terraform mirror probe for Cloud.ru NLB

Use this when Cloud.ru Compute/VPC API reads do not clearly show whether an NLB is internet-facing.

## Why this path matters

In a live project, the following mismatch occurred:
- Compute interfaces showed only private `lbaas-reserve-*` VIP addresses.
- `floating-ips` showed only a NAT gateway public IP.
- This initially suggested the LB was internal-only.
- The real NLB object, queried through the Terraform provider data source, showed `external_address.ipv4 = 37.44.196.221`.
- A live HTTP probe confirmed that the public IP was working and balancing across both backend VMs.

Lesson:
- Do not conclude `internal-only` from Compute alone.
- Query the NLB service object directly.

## Read-only Terraform data sources

Use:
- `cloudru_evolution_nlb_network_load_balancer_collection`
- `cloudru_evolution_nlb_target_group_collection`

Important fields to inspect:
- `balancers[].name`
- `balancers[].id`
- `balancers[].external_address.ipv4`
- `balancers[].internal_address.ipv4`
- `balancers[].status`
- `balancers[].rules[].listeners[].port`
- `balancers[].rules[].listeners[].target_port`
- `balancers[].rules[].health_check`
- `balancers[].rules[].target_group_id`
- `target_groups[].target_vms[]`

## Local mirror setup pattern

If plain `terraform init` fails with:
- `Invalid provider registry host`

use a filesystem mirror with the provider binary from the Cloud.ru GitHub release.

Working pattern:
1. Download Terraform locally.
2. Download provider binary from the tagged GitHub release, for example:
   - `terraform-provider-cloud_2.1.1_linux_amd64`
3. Place it under:
   - `/tmp/tf-mirror/cloud.ru/cloudru/cloud/2.1.1/linux_amd64/terraform-provider-cloud_v2.1.1`
4. Create `TF_CLI_CONFIG_FILE` with:

```hcl
provider_installation {
  filesystem_mirror {
    path    = "/tmp/tf-mirror"
    include = ["cloud.ru/cloudru/cloud"]
  }
  direct {
    exclude = ["cloud.ru/cloudru/cloud"]
  }
}
```

5. Initialize Terraform with that config file.

## Live pattern confirmed in this session

NLB object:
- `name`: `lbaas-app-external`
- `id`: `4c10e11d-79fb-46e5-8df5-2a18fdaf2689`
- `external_address.ipv4`: `37.44.196.221`
- `internal_address.ipv4`: `192.168.100.171`
- `status`: `NLB_STATUS_RUNNING`
- listener: `80 -> 80`
- health check: TCP on `80`
- target group: `vm-group-app-external`

Target group contained:
- `vm-app-external1`
- `vm-app-external2`

Live public probe results:
- `http://37.44.196.221/` returned `200 OK`
- repeated requests hit both backend pages
- `443` returned `Connection refused`
- `22` returned `Connection refused`

## Correct conclusion for this pattern

The LB is healthy and internet-facing for HTTP on port `80`.

If the user says `external IP does not work`, check whether they actually mean one of these:
- they tried `https://` while only `80` is configured;
- they expected direct host access through the LB IP;
- they expected another port such as `443` or `8080` that has no listener.
