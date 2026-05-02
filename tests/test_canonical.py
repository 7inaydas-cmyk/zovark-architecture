"""
Tests for zovark.slice001.canonical — canonical JSON serialization.

Task 2.3 acceptance criteria:
- Two dicts with same content, different insertion order → byte-identical output.
- Nested object with array → keys sorted at every level.
- Timestamp string with Z passes through unchanged.
"""

import math
import pytest

from zovark.slice001.canonical import canonical_json


# ---------------------------------------------------------------------------
# Key ordering
# ---------------------------------------------------------------------------

class TestKeyOrdering:
    def test_same_content_different_insertion_order_is_byte_identical(self):
        """AC: Two dicts with same content, different insertion order → byte-identical."""
        a = {"z": 1, "a": 2, "m": 3}
        b = {"a": 2, "m": 3, "z": 1}
        assert canonical_json(a) == canonical_json(b)

    def test_keys_sorted_lexicographically(self):
        """Keys appear in Unicode code-point order in the output."""
        obj = {"z": 1, "a": 2}
        result = canonical_json(obj).decode("utf-8")
        assert result == '{"a":2,"z":1}'

    def test_nested_object_keys_sorted_at_every_level(self):
        """AC: Nested object with array → keys sorted at every level."""
        obj = {
            "z": {"b": [3, 1, 2], "a": 0},
            "a": {"y": "yes", "x": "no"},
        }
        result = canonical_json(obj).decode("utf-8")
        # Outer keys: a before z.
        # Inner keys of "a": x before y.
        # Inner keys of "z": a before b.
        assert result == '{"a":{"x":"no","y":"yes"},"z":{"a":0,"b":[3,1,2]}}'

    def test_unicode_key_ordering(self):
        """Keys are sorted by Unicode code point, not locale."""
        # Uppercase letters (U+0041…) sort before lowercase (U+0061…).
        obj = {"b": 1, "A": 2}
        result = canonical_json(obj).decode("utf-8")
        assert result == '{"A":2,"b":1}'


# ---------------------------------------------------------------------------
# Scalar types
# ---------------------------------------------------------------------------

class TestScalars:
    def test_null(self):
        assert canonical_json(None) == b"null"

    def test_true(self):
        assert canonical_json(True) == b"true"

    def test_false(self):
        assert canonical_json(False) == b"false"

    def test_integer(self):
        assert canonical_json(42) == b"42"

    def test_negative_integer(self):
        assert canonical_json(-7) == b"-7"

    def test_zero(self):
        assert canonical_json(0) == b"0"

    def test_finite_float(self):
        result = canonical_json(3.14)
        # Must be valid JSON bytes representing 3.14.
        import json
        assert json.loads(result) == pytest.approx(3.14)

    def test_nan_raises(self):
        with pytest.raises(ValueError, match="NaN"):
            canonical_json(float("nan"))

    def test_inf_raises(self):
        with pytest.raises(ValueError, match="Infinity"):
            canonical_json(float("inf"))

    def test_neg_inf_raises(self):
        with pytest.raises(ValueError, match="Infinity"):
            canonical_json(float("-inf"))

    def test_bool_not_treated_as_int(self):
        """bool is a subclass of int in Python; must serialize as true/false."""
        assert canonical_json(True) == b"true"
        assert canonical_json(False) == b"false"
        # Confirm it is NOT "1" or "0".
        assert canonical_json(True) != b"1"
        assert canonical_json(False) != b"0"


# ---------------------------------------------------------------------------
# Strings
# ---------------------------------------------------------------------------

class TestStrings:
    def test_simple_string(self):
        assert canonical_json("hello") == b'"hello"'

    def test_timestamp_with_z_passes_through_unchanged(self):
        """AC: Timestamp string with Z passes through unchanged."""
        ts = "2026-05-01T10:00:00Z"
        result = canonical_json(ts).decode("utf-8")
        # The string value itself must be preserved verbatim inside the quotes.
        assert result == f'"{ts}"'

    def test_timestamp_without_z_passes_through(self):
        """Strings are not validated as timestamps — they pass through as-is."""
        ts = "2026-05-01T10:00:00+00:00"
        result = canonical_json(ts).decode("utf-8")
        assert result == f'"{ts}"'

    def test_string_with_special_chars_is_escaped(self):
        result = canonical_json('say "hi"').decode("utf-8")
        assert result == r'"say \"hi\""'

    def test_unicode_string(self):
        result = canonical_json("café").decode("utf-8")
        assert result == '"café"'


# ---------------------------------------------------------------------------
# Arrays
# ---------------------------------------------------------------------------

class TestArrays:
    def test_array_preserves_insertion_order(self):
        """AC: Arrays preserve insertion order."""
        arr = [3, 1, 2]
        assert canonical_json(arr) == b"[3,1,2]"

    def test_empty_array(self):
        assert canonical_json([]) == b"[]"

    def test_nested_array(self):
        assert canonical_json([[1, 2], [3, 4]]) == b"[[1,2],[3,4]]"

    def test_array_of_dicts_keys_sorted(self):
        arr = [{"b": 2, "a": 1}]
        assert canonical_json(arr) == b'[{"a":1,"b":2}]'


# ---------------------------------------------------------------------------
# Compact output (no whitespace)
# ---------------------------------------------------------------------------

class TestCompact:
    def test_no_spaces_in_output(self):
        obj = {"a": 1, "b": [1, 2]}
        result = canonical_json(obj).decode("utf-8")
        assert " " not in result

    def test_no_trailing_newline(self):
        result = canonical_json({"a": 1})
        assert not result.endswith(b"\n")
        assert not result.endswith(b" ")


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_object_called_twice_is_identical(self):
        obj = {"z": [1, 2], "a": {"x": True, "y": None}}
        assert canonical_json(obj) == canonical_json(obj)

    def test_equivalent_objects_produce_identical_bytes(self):
        """The core property: same logical content → same bytes regardless of
        how the dict was constructed."""
        x = dict(b=2, a=1)
        y = {"a": 1, "b": 2}
        assert canonical_json(x) == canonical_json(y)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrors:
    def test_unsupported_type_raises_type_error(self):
        with pytest.raises(TypeError):
            canonical_json(object())

    def test_set_raises_type_error(self):
        with pytest.raises(TypeError):
            canonical_json({1, 2, 3})

    def test_nan_inside_list_raises(self):
        with pytest.raises(ValueError):
            canonical_json([1, float("nan"), 3])

    def test_nan_inside_dict_raises(self):
        with pytest.raises(ValueError):
            canonical_json({"a": float("nan")})
