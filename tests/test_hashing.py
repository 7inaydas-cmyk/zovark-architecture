"""
Tests for zovark.slice001.hashing — SHA-256 helpers.

Task 2.4 acceptance criteria:
- sha256_of_string("genesis") → known golden hex value.
- sha256_of_obj({"b": 1, "a": 2}) equals sha256_of_obj({"a": 2, "b": 1}).

Note on the golden value:
  sha256("genesis".encode("utf-8")) = aeebad4a796fcc2e15dc4c6061b45ed9b373f26adfc798ca7d2d8cc58182718e
  Verified with: python3 -c "import hashlib; print(hashlib.sha256(b'genesis').hexdigest())"
"""

import hashlib

from zovark.slice001.hashing import sha256_hex, sha256_of_obj, sha256_of_string


# ---------------------------------------------------------------------------
# sha256_hex
# ---------------------------------------------------------------------------

class TestSha256Hex:
    def test_known_input(self):
        """sha256_hex(b"") is the well-known SHA-256 of the empty byte string."""
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert sha256_hex(b"") == expected

    def test_returns_lowercase_hex(self):
        result = sha256_hex(b"hello")
        assert result == result.lower()
        assert all(c in "0123456789abcdef" for c in result)

    def test_length_is_64_chars(self):
        assert len(sha256_hex(b"anything")) == 64

    def test_different_inputs_produce_different_digests(self):
        assert sha256_hex(b"a") != sha256_hex(b"b")

    def test_same_input_is_deterministic(self):
        assert sha256_hex(b"zovark") == sha256_hex(b"zovark")


# ---------------------------------------------------------------------------
# sha256_of_string
# ---------------------------------------------------------------------------

class TestSha256OfString:
    # Golden value: sha256("genesis".encode("utf-8"))
    GENESIS_GOLDEN = "aeebad4a796fcc2e15dc4c6061b45ed9b373f26adfc798ca7d2d8cc58182718e"

    def test_genesis_golden_value(self):
        """AC: sha256_of_string("genesis") → known golden hex value."""
        assert sha256_of_string("genesis") == self.GENESIS_GOLDEN

    def test_matches_hashlib_directly(self):
        """sha256_of_string must agree with hashlib on the same UTF-8 encoding."""
        s = "hello world"
        expected = hashlib.sha256(s.encode("utf-8")).hexdigest()
        assert sha256_of_string(s) == expected

    def test_empty_string(self):
        expected = hashlib.sha256(b"").hexdigest()
        assert sha256_of_string("") == expected

    def test_unicode_string(self):
        s = "café"
        expected = hashlib.sha256(s.encode("utf-8")).hexdigest()
        assert sha256_of_string(s) == expected

    def test_deterministic(self):
        assert sha256_of_string("zovark") == sha256_of_string("zovark")


# ---------------------------------------------------------------------------
# sha256_of_obj
# ---------------------------------------------------------------------------

class TestSha256OfObj:
    def test_key_order_does_not_affect_digest(self):
        """AC: sha256_of_obj({"b": 1, "a": 2}) equals sha256_of_obj({"a": 2, "b": 1})."""
        assert sha256_of_obj({"b": 1, "a": 2}) == sha256_of_obj({"a": 2, "b": 1})

    def test_different_values_produce_different_digests(self):
        assert sha256_of_obj({"a": 1}) != sha256_of_obj({"a": 2})

    def test_different_keys_produce_different_digests(self):
        assert sha256_of_obj({"a": 1}) != sha256_of_obj({"b": 1})

    def test_nested_object_key_order_does_not_affect_digest(self):
        x = {"outer": {"z": 1, "a": 2}}
        y = {"outer": {"a": 2, "z": 1}}
        assert sha256_of_obj(x) == sha256_of_obj(y)

    def test_array_order_does_affect_digest(self):
        """Arrays preserve insertion order — different order → different digest."""
        assert sha256_of_obj([1, 2, 3]) != sha256_of_obj([3, 2, 1])

    def test_null_value(self):
        result = sha256_of_obj(None)
        expected = hashlib.sha256(b"null").hexdigest()
        assert result == expected

    def test_deterministic(self):
        obj = {"z": [1, 2], "a": {"x": True, "y": None}}
        assert sha256_of_obj(obj) == sha256_of_obj(obj)

    def test_matches_canonical_json_then_sha256(self):
        """sha256_of_obj must equal sha256_hex(canonical_json(obj))."""
        from zovark.slice001.canonical import canonical_json
        obj = {"b": 99, "a": "hello"}
        expected = hashlib.sha256(canonical_json(obj)).hexdigest()
        assert sha256_of_obj(obj) == expected

    def test_genesis_string_via_obj(self):
        """sha256_of_obj("genesis") hashes the JSON string '"genesis"',
        which is different from sha256_of_string("genesis")."""
        from zovark.slice001.canonical import canonical_json
        expected = hashlib.sha256(canonical_json("genesis")).hexdigest()
        assert sha256_of_obj("genesis") == expected
        # Confirm it differs from sha256_of_string("genesis").
        assert sha256_of_obj("genesis") != sha256_of_string("genesis")
