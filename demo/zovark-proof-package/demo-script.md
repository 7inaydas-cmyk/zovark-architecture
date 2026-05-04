# Zovark — 90-Second Screen Recording Script

**Format:** terminal + file viewer side by side
**Audience:** YC partners, MSSP evaluators, SOC managers
**Goal:** Show the proof package before the SOC approves host isolation

---

## Setup (before recording)

Open two panes:
- Left: terminal in `demo/zovark-proof-package/`
- Right: file viewer (VS Code, bat, or any Markdown renderer)

Have these files ready to open instantly:
1. `out/tape-001/customer-report.md`
2. `out/tape-001/edr-handoff.json`
3. `out/tape-001/replay-report.json`

---

## Recording script

---

**[0:00 — 0:10] The raw alert**

*Show in terminal:*
```
cat samples/edr/phishing-powershell.json
```

*Say:*
> "This is the raw EDR alert. Word spawned a hidden PowerShell with an encoded
> command. Your AI system says: isolate HOST-12. Before anyone approves that,
> here is what Zovark produces."

---

**[0:10 — 0:30] Open the proof report — action card first**

*Open `out/tape-001/customer-report.md`. Scroll to the top.*

*Say:*
> "The first thing your analyst sees is the action card."

*Read aloud:*
> "Action: ISOLATE_HOST. Target: HOST-12. Approval required: YES — nothing has
> been dispatched. Verdict: CONFIRMED_MALICIOUS. Reversibility: reversible by EDR —
> automatic release available."

*Pause one beat.*

> "Before your analyst clicks approve, they know exactly what is being recommended,
> why, and that it can be undone."

---

**[0:30 — 0:50] Evidence and blast radius**

*Scroll to section 2 (evidence table) and section 6 (blast radius).*

*Say:*
> "Five evidence items. Each one has a SHA-256 hash of its exact content — the
> process event, the network connection, the LSASS access, the lateral movement
> attempt. These are not summaries. They are the specific bytes that justified
> the recommendation."

*Scroll to blast radius.*

> "And before approving: HOST-12 only. No shared infrastructure. The lateral
> movement to HOST-13 was already blocked. Single workstation isolation."

---

**[0:50 — 1:10] The action card and reversal plan**

*Open `out/tape-001/edr-handoff.json`. Show `approval_mode`, `blast_radius`,
and `reversal_or_recovery_plan`.*

*Say:*
> "The action card. Approval mode: approval_required. Nothing dispatches without
> a human. And the reversal plan is right here — reversible by EDR, automatic
> release_isolation, four-hour window. Your analyst knows the exit before they
> approve the entry."

---

**[1:10 — 1:25] Replay verification**

*Open `out/tape-001/replay-report.json`. Show the top of `replay_state`.*

*Say:*
> "Replay result: succeeded. Five evidence hashes verified. Verdict recomputed:
> confirmed_malicious. Matches. No live LLM call. No live EDR call. This proof
> package is self-contained — an auditor can verify it offline, six months from
> now, without access to any live system."

---

**[1:25 — 1:30] Close**

*Say:*
> "That is the proof package. Evidence, verdict, approval gate, blast radius,
> reversal plan, and replayable verification — before anyone clicks approve.
> We are looking for design partners to review this format with us."

---

## Notes for the presenter

- Do not apologize for the static nature of the demo. The hashes are real. The
  chain is real. The format is the product.
- If asked "is this live?": "This is a static demo package showing the intended
  output shape. The pipeline that generates it automatically is being built now.
  The architecture is frozen and evidence-backed."
- If asked about the encoded PowerShell command: the base64 decodes to a
  `WebClient.DownloadFile` call fetching a payload from 192.168.1.100. You can
  decode it live if the audience wants to see it.
- Keep the replay section brief. The key claim is: same evidence, same rules,
  same verdict, verifiable offline. That is the moat.
