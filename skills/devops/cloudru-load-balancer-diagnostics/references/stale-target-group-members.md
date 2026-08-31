# Stale target-group members after VM recreation

Use this note when a Cloud.ru Evolution NLB appears healthy but traffic to the LB VIP still resets or behaves inconsistently.

## Confirmed pattern

Observed in project `6649fb7f-140c-401a-9420-16948b8aa5aa`:

- Internal LB object was healthy:
  - name: `lbaas-app-internal`
  - internal VIP: `192.168.0.97`
  - listener: `80 -> 80`
  - health check: TCP on `80`
- Security groups allowed traffic from `sg-admin-internal` to `sg-app-internal`.
- Admin VM in the same subnet could reach backend IPs `192.168.0.5` and `192.168.0.6` at least partially.
- But `curl http://192.168.0.97/` from the admin VM returned:
  - `curl: (56) Recv failure: Connection reset by peer`

## Root-cause pattern

The LB target group can retain stale backend objects after VM recreation or replacement.
Displayed VM names may still look correct, but the effective target-group membership is tracked by VM ID and interface ID.

Example mismatch:

Current live backend VMs:
- `vm-app-internal1` -> VM ID `6e77e2df-159c-411f-9003-d5ab1828570e` -> interface IP `192.168.0.5`
- `vm-app-internal2` -> VM ID `efae2a09-d12b-4b7d-8f18-434c275cd49a` -> interface IP `192.168.0.6`

But target group `vm-group-app-internal` still contained different member IDs:
- `2313236d-34f0-4626-9e76-323b40aa687c`
- `c87667a3-9149-4a96-bf5c-0b02b4f79696`

## Practical check sequence

1. Read the NLB object and capture `target_group_id`.
2. Read the target group and record member VM IDs/interface IDs.
3. Independently list current compute VMs and interfaces.
4. Match by VM ID and interface ID, not by names only.
5. If IDs differ, treat the target group as stale even if names/roles still look right.

## Practical conclusion

When this mismatch exists, stop treating the incident as generic SG/routing failure.
The highest-value next action is to refresh target-group membership to the current VM/interface objects.
