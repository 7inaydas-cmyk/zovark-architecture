## 1. Update the binding spec

- [ ] 1.1 The MODIFIED Requirements blocks in this change update `openspec/specs/investigation-tape/spec.md` on archive.
- [ ] 1.2 Run `openspec validate fix-tape-replay-relationship`.

## 2. Update derived docs

- [ ] 2.1 Edit `architecture/objects/investigation-tape.md`: remove the `replay_state_ref` row from the field table; update the lifecycle section to show `recording → closed` (one-way; no `replaying` state); remove the `replay_state_ref` reference from the customer-facing surface description.
- [ ] 2.2 Edit `architecture/one-page-architecture.md` line 26: remove `replay_state_ref` from the Investigation Tape field list; update the lifecycle notation to `recording → closed`.

## 3. Capture the spec

- [ ] 3.1 Run `openspec archive fix-tape-replay-relationship --yes`.

## 4. Verify enforcement scripts still pass

- [ ] 4.1 Run `python3 scripts/check_mvp_scope_consistency.py`. Confirm pass.
- [ ] 4.2 Run `python3 scripts/check_claim_provenance.py`. Confirm pass.
- [ ] 4.3 Run `python3 scripts/check_adr_cross_links.py`. Confirm pass.

## 5. Commit and push

- [ ] 5.1 Stage the change archive, the updated binding spec, the architecture object doc, and the one-pager.
- [ ] 5.2 Commit: "Fix tape-replay relationship — drop 'replaying' tape state and replay_state_ref drift".
- [ ] 5.3 Push.
