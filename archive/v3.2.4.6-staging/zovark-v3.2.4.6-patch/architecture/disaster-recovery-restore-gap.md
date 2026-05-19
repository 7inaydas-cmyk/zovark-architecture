# Disaster Recovery Restore-Gap Semantics

This patch tree does not implement disaster recovery, PITR, audit-chain restore verification, or offboarding runtime behavior. `invariants.md` is the authoritative home for this restore-gap rule; this document is a focused reference for engineering handoff.

The following rule is mandatory for any future DR design:

A valid post-restore audit chain proves internal consistency of the recovered chain. It does not prove that no data loss occurred.

## Required Audit Event

Future audit-chain schemas must include `DISASTER_RECOVERY_RESTORE_COMPLETED` with this payload:

- `restore_started_at_ns`
- `restore_completed_at_ns`
- `restored_to_lsn`
- `restored_to_timestamp`
- `pre_restore_latest_root_hash_if_available`
- `post_restore_chain_root`
- `known_data_loss_window_start`
- `known_data_loss_window_end`
- `operator_id`
- `incident_id`

## Required Verifier State

If audit-chain verification is defined, it must include:

- `VALID_AFTER_RESTORE_WITH_DECLARED_GAP`

This state means the recovered chain is internally consistent from the restore point forward and explicitly declares the possible loss window.
