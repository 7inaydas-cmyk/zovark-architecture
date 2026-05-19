#!/bin/bash
# Run all v3.2.4.6 ship-time tests and emit transcript to stdout.
#
# v3.2.4.6: PYTHONDONTWRITEBYTECODE=1 prevents Python from creating
# __pycache__ directories during the run, which would fail subsequent
# check_patch_self_test invocations (because __pycache__ files would be
# present on disk but not in PATCH-MANIFEST.json).
set +e
export PYTHONDONTWRITEBYTECODE=1
cd "$(dirname "$0")/.."
PATCH=$(pwd)
RC_TOTAL=0

echo "==================================================================="
echo "Zovark v3.2.4.6 — ship-time evidence transcript"
echo "==================================================================="
echo ""

echo "[1/5] check_release_metadata_consistency_v3245"
echo "----------------------------------------------"
python3 scripts/check_release_metadata_consistency_v3245.py 2>&1
RC=$?
echo "(exit $RC)"
[ $RC -eq 0 ] || RC_TOTAL=1
echo ""

echo "[2/5] check_control_plane_schemas_present (REAL fixtures, no markers)"
echo "---------------------------------------------------------------------"
echo "  pass.fixture (must exit 0):"
python3 scripts/check_control_plane_schemas_present.py \
  --fixture-root tests/bootstrap-fixtures/control_plane_schemas_present/pass.fixture
PASS_RC=$?
echo "  -> exit $PASS_RC"
echo "  fail.fixture (must exit non-zero):"
FAIL_OUT=$(python3 scripts/check_control_plane_schemas_present.py \
  --fixture-root tests/bootstrap-fixtures/control_plane_schemas_present/fail.fixture 2>&1)
FAIL_RC=$?
if [ $FAIL_RC -ne 0 ]; then
  echo "EXPECTED-FAIL: ${FAIL_OUT#FAIL: }"
else
  echo "$FAIL_OUT"
fi
echo "  -> exit $FAIL_RC"
if [ $PASS_RC -eq 0 ] && [ $FAIL_RC -ne 0 ]; then
  echo "  RESULT: OK"
else
  echo "  RESULT: SHIP-TIME FAIL"
  RC_TOTAL=1
fi
echo ""

echo "[3/5] check_telemetry_boundary_schema_present (REAL fixtures, no markers)"
echo "-------------------------------------------------------------------------"
echo "  pass.fixture (must exit 0):"
python3 scripts/check_telemetry_boundary_schema_present.py \
  --fixture-root tests/bootstrap-fixtures/telemetry_boundary_schema_present/pass.fixture
PASS_RC=$?
echo "  -> exit $PASS_RC"
echo "  fail.fixture (must exit non-zero):"
FAIL_OUT=$(python3 scripts/check_telemetry_boundary_schema_present.py \
  --fixture-root tests/bootstrap-fixtures/telemetry_boundary_schema_present/fail.fixture 2>&1)
FAIL_RC=$?
if [ $FAIL_RC -ne 0 ]; then
  echo "EXPECTED-FAIL: ${FAIL_OUT#FAIL: }"
else
  echo "$FAIL_OUT"
fi
echo "  -> exit $FAIL_RC"
if [ $PASS_RC -eq 0 ] && [ $FAIL_RC -ne 0 ]; then
  echo "  RESULT: OK"
else
  echo "  RESULT: SHIP-TIME FAIL"
  RC_TOTAL=1
fi
echo ""

echo "[4/5] Schema example validation (6 pass + 10 fail, including new contract negatives)"
echo "------------------------------------------------------------------------------------"
ALL_OK=true
declare -a EXAMPLES=(
  "update_candidate.pass:VALID"
  "update_candidate.fail:INVALID"
  "update_bundle_signed.pass:VALID"
  "update_bundle_signed.fail:INVALID"
  "update_bundle_signed.fail_same_role:INVALID"
  "research_experiment_result.pass:VALID"
  "research_experiment_result.fail:INVALID"
  "control_plane_instance_status.pass:VALID"
  "control_plane_instance_status.fail:INVALID"
  "telemetry_envelope.pass:VALID"
  "telemetry_envelope.fail:INVALID"
  "telemetry_envelope.fail_kind_mismatch:INVALID"
  "update_promotion_decision.pass:VALID"
  "update_promotion_decision.fail:INVALID"
  "update_promotion_decision.fail_tier3_no_security:INVALID"
  "update_promotion_decision.fail_tier3_short_soak:INVALID"
)
for entry in "${EXAMPLES[@]}"; do
  IFS=':' read -r stem expected <<< "$entry"
  schema_name="${stem%%.*}"
  out=$(python3 scripts/jsonschema_minimal.py \
    "architecture/blueprint/schemas/$schema_name.schema.json" \
    "architecture/blueprint/schemas/examples/$stem.json" 2>&1)
  rc=$?
  if [ "$expected" = "VALID" ] && [ $rc -eq 0 ]; then
    printf "  %-58s OK\n" "$stem (expect VALID)"
  elif [ "$expected" = "INVALID" ] && [ $rc -ne 0 ]; then
    printf "  %-58s OK  (reason: %s)\n" "$stem (expect INVALID)" "${out#INVALID: }"
  else
    printf "  %-58s SHIP-TIME FAIL  expected=%s got_rc=%d\n" "$stem" "$expected" "$rc"
    ALL_OK=false
  fi
done
if $ALL_OK; then
  echo "  RESULT: all 16 examples behave as intended"
else
  echo "  RESULT: SHIP-TIME FAIL"
  RC_TOTAL=1
fi
echo ""

echo "[5/5] check_patch_self_test"
echo "---------------------------"
echo "  This step is INTENTIONALLY OMITTED from the transcript because the"
echo "  self-test verifies the manifest hash of every file including this"
echo "  transcript itself, which creates a content-vs-hash chicken-and-egg."
echo "  The self-test is run separately by the apply script and by anyone"
echo "  invoking 'scripts/check_patch_self_test.py --patch-root .' against"
echo "  the unpacked patch."
echo ""

echo "==================================================================="
echo "End ship-time transcript."
echo ""
echo "Note: the customer's POST-APPLY transcript (verify-bootstrap.sh +"
echo "bootstrap-acceptance.sh on the patched repo) is a separate artifact"
echo "produced after Step 8 of PATCH-README.md. This ship-time transcript"
echo "covers the patch artifact only, not the post-apply repo."
echo "==================================================================="
exit $RC_TOTAL
