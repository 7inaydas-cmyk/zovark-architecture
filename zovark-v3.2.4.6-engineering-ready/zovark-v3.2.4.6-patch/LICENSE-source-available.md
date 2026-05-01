# Zovark Source-Available License v1.0

**Status:** DRAFT — pending founder sign-off via M1-DECISION-001 (ADR-0043 acceptance).
**Effective:** This license has no legal effect until the corresponding ADR-0043 is moved from `PROPOSED-STRATEGIC-PIVOT` to `ACCEPTED` and a final reviewed version of this license file is committed and tagged.

> This draft supports ADR-0043 because the ADR names the Tier B source-available license. ADR-0043 is the strategic-pivot ADR; the license is its operational complement. Both must be accepted together. A qualified attorney must review this draft before founder sign-off; the language below is a starting point, not legal advice.

---

## Preamble

This License governs use of the Zovark Tier B source code: the customer-runtime implementation that runs inside customer environments. It is a source-available license, not an open-source license. It exists because:

- Customers in regulated industries require the right to read, audit, and modify the code that processes their data. Closed-source binaries do not satisfy this requirement.
- Zovark must retain the ability to maintain a sustainable commercial product. A fully open-source runtime invites verbatim forks that compete with Zovark without contributing to its maintenance.

Tier A code (canonical schemas, standards registry, ADRs, invariants, verifier scripts, and the `zovark update verify` CLI source) is licensed under Apache-2.0 separately and is not subject to this License. See `LICENSE` for Apache-2.0 terms.

Tier C code (Zovark-internal hosted systems including Control Plane, Update Factory, Research Pipeline) is not distributed and is not subject to this License.

## 1. Definitions

**"Software"** means the source code, object code, configuration, and documentation distributed under this License, identified by a `LICENSE-source-available.md` file at its repository root or by a SPDX identifier of `LicenseRef-Zovark-Source-Available-1.0`.

**"You"** means the natural person or legal entity exercising rights under this License.

**"Customer Environment"** means infrastructure operated by You or on Your behalf for the purpose of processing Your own organization's data. It does not include infrastructure operated to process the data of third parties as a service.

**"Zovark"** means the entity that publishes the Software (the corporate entity that owns the `zovark/zovark-core` repository or its successor).

**"Modifications"** means changes to the Software, including additions, deletions, and derivative works.

**"Distribute"** means to make available to a third party, whether by network transmission, physical media, or other means, including making accessible via an API or hosted service.

## 2. Grant of Rights

Subject to the conditions and limitations of this License, Zovark grants You a worldwide, non-exclusive, royalty-free license to:

1. **Read** the Software for any purpose, including security audit, code review, and academic study.
2. **Run** the Software in Your Customer Environment to process Your own organization's data.
3. **Modify** the Software for use in Your Customer Environment.
4. **Make security disclosures** about the Software, in accordance with `SECURITY-VULN-DISCLOSURE.md`.

## 3. Conditions

The grant in Section 2 is conditional on:

1. **No third-party hosting.** You may not Distribute the Software, or any Modification, to a third party as a service that processes that third party's data. Operating Zovark inside Your Customer Environment to process Your own data is permitted; running it as a multi-tenant service for others is not.
2. **No competing-product distribution.** You may not Distribute the Software, or any Modification, as a product that competes with Zovark's commercial offering. "Compete" here means: marketed or sold as a substitute for Zovark's commercial product.
3. **Notices preserved.** You must preserve all copyright, license, and attribution notices in the Software and in any Modification You Distribute under permitted terms.
4. **Modifications marked.** Any Modification You Distribute under permitted terms must be clearly identified as a Modification and must not misrepresent its origin.
5. **No removal of update-verification.** You may not remove or disable the signature-verification, attestation-verification, or telemetry-boundary mechanisms (per ADR-0039, ADR-0041, ADR-0042) when running the Software in production. You may disable them in non-production builds for testing.

## 4. Permitted Distribution

The conditions in Section 3 do not prohibit:

1. **Source mirroring** to Your own organization's private repositories for backup, audit, or internal review purposes.
2. **Modification distribution** to Your own personnel, contractors, or auditors for purposes consistent with Your operation of the Software in Your Customer Environment.
3. **Security research disclosures** describing vulnerabilities in the Software, including reproduction steps and proof-of-concept code, made in accordance with `SECURITY-VULN-DISCLOSURE.md`.
4. **Academic publication** describing the Software, including code excerpts as needed to support analysis.
5. **Contributions back to Zovark.** You may submit Modifications to Zovark under a Contributor License Agreement; such contributions, if accepted, may be redistributed by Zovark under any license terms Zovark chooses.

## 5. Trademark

This License does not grant You rights to use Zovark's trademarks, service marks, or logos, except as required for accurate reference to the Software's origin.

## 6. Patent License

Zovark grants You a non-exclusive, royalty-free patent license to the patent claims Zovark holds that are necessarily infringed by Your permitted use of the Software, limited to such permitted use. This patent license terminates if You initiate patent litigation against Zovark or any Zovark customer alleging that the Software infringes a patent.

## 7. Disclaimer of Warranty

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.

## 8. Limitation of Liability

IN NO EVENT SHALL ZOVARK BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 9. Termination

This License terminates automatically if You materially breach Section 3. On termination:

1. You must cease all use of the Software within 90 days.
2. Distributions made to Your personnel under Section 4.2 may continue solely for the purpose of an orderly cessation, not exceeding 90 days.
3. Sections 5, 7, and 8 survive termination.

Zovark may also terminate this License with respect to a specific version of the Software by issuing a successor version under different terms; such termination does not affect Your prior compliant use of earlier versions.

## 10. Conversion

If, after a period defined by Zovark in writing (the "Conversion Period"), Zovark elects to relicense a particular version of the Software under an OSI-approved open-source license, this License's restrictions on that version cease to apply and the OSI-approved license governs.

## 11. Governing Law

This License is governed by the laws specified in the corresponding Master Agreement between You and Zovark, or, in the absence of such agreement, by the laws of the jurisdiction of Zovark's principal place of business.

## 12. SPDX Identifier

```
LicenseRef-Zovark-Source-Available-1.0
```

---

## Drafting notes (remove before founder sign-off)

The following notes are for the founder and counsel; they are not part of the License text:

1. Section 3.1's "no third-party hosting" clause is the BSL-style restriction; the language deliberately avoids the phrase "Business Source License" and avoids BSL's automatic-conversion-to-Apache rule. Section 10 ("Conversion") gives Zovark optional, not automatic, conversion.

2. Section 3.2's "no competing-product distribution" is broad. Counsel should narrow it for the specific commercial offering Zovark intends to protect, ideally with a defined Production Use clause.

3. Section 3.5's no-removal-of-update-verification clause is unusual. It exists because the trust contract for Zovark depends on signature verification being intact. Counsel should review whether this clause is enforceable under the law of the chosen forum.

4. Section 6's patent license should be reviewed against ADR-0042's defensive patent posture. If Zovark joins a defensive patent pool, this section may need to reference the pool.

5. Section 9's 90-day cessation period is a working number. Adjust per counsel's recommendation.

6. The SPDX identifier `LicenseRef-Zovark-Source-Available-1.0` is the form used by SPDX for non-OSI custom licenses. After SPDX listing (if pursued), this may become a registered identifier.

7. This License does not apply to canonical schemas (Apache-2.0 per ADR-0010), the standards registry, or any ADR/invariant/verifier-script content; those remain Tier A and are governed by the separate `LICENSE` file at the repository root.

---

**Final note:** Until ADR-0043 is `ACCEPTED` and this License is reviewed by counsel and finalized, the runtime code is not distributed under this License. The Tier B license is gated on M1-DECISION-001.
