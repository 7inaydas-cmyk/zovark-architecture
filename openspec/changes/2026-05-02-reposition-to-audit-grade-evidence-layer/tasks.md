## 1. Update product-wedge spec

- [x] 1.1 Modify `openspec/specs/product-wedge/spec.md`: split into internal and
  external canonical statements; add hero artifact requirement; update all scenarios.

## 2. Update architecture documents

- [x] 2.1 Modify `architecture/source-of-truth.md`: update "Current product wedge"
  section to include both internal and external statements.
- [x] 2.2 Modify `architecture/one-page-architecture.md`: update §1 (Product wedge)
  to show both statements; update §7 (Build rule) to include external phrasing.

## 3. Update Slice 001 spec framing

- [x] 3.1 Modify `.kiro/specs/slice-001-investigation-tape/requirements.md`:
  update overview to lead with proof package framing; update build rule reference.
- [x] 3.2 Modify `.kiro/specs/slice-001-investigation-tape/design.md`:
  update `customer-report.md` structure in §8 to lead with EDR action card.

## 4. Create YC positioning doc

- [x] 4.1 Write `docs/yc-positioning.md` per design §YC positioning doc.

## 5. Create Slice 001 demo script

- [x] 5.1 Write `docs/slice-001-demo-script.md` per design §Slice 001 demo script.

## 6. Create MSSP outreach doc

- [x] 6.1 Write `docs/mssp-outreach.md` per design §MSSP outreach doc.

## 7. Verify no architecture enforcement scripts are broken

- [ ] 7.1 Run `python scripts/check_mvp_scope_consistency.py` — confirm pass.
- [ ] 7.2 Run `python scripts/check_claim_provenance.py` — confirm pass.
- [ ] 7.3 Run `python scripts/check_adr_cross_links.py` — confirm pass (bootstrap mode).
- [ ] 7.4 Confirm no architecture object files (`architecture/objects/*.md`) were
  modified by this change.
- [ ] 7.5 Confirm no `openspec/specs/investigation-tape/spec.md`,
  `openspec/specs/edr-handoff/spec.md`, or `openspec/specs/replay-and-audit/spec.md`
  were modified by this change.
