## 1. Implement the script

- [ ] 1.1 Add `scripts/check_adr_cross_links.py` matching the interface in `openspec/specs/adr-cross-link/spec.md` (as MODIFIED by this change). Auto-detect mode based on filesystem state.
- [ ] 1.2 Make it executable: `chmod +x scripts/check_adr_cross_links.py`.
- [ ] 1.3 Run it in current state (bootstrap mode): `python3 scripts/check_adr_cross_links.py`. Verify exit 0 and the banner lists the 8 baseline ADRs awaiting post-apply verification.

## 2. Capture the spec

- [ ] 2.1 Run `openspec validate fix-adr-cross-link-enforcement`.
- [ ] 2.2 Run `openspec archive fix-adr-cross-link-enforcement --yes`.

## 3. Commit and push

- [ ] 3.1 Stage `scripts/check_adr_cross_links.py`, the change archive, and the updated spec.
- [ ] 3.2 Commit: "Implement ADR cross-link verification script with bootstrap-mode".
- [ ] 3.3 Push.
