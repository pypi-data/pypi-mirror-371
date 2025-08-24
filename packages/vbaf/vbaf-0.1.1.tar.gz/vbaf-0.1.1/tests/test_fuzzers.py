import pytest
from vbaf.fuzzers import VBAF


@pytest.fixture
def sample_fuzzer():
    tokens = [str(i) for i in range(10)]
    return VBAF(vocabulary=tokens, n_size=10, rand_bounds=(2, 5), seed=42)


def test_generate_fuzzy_payload_contains_payload(sample_fuzzer: VBAF):
    """Check if the generated payload contains the injected string always."""
    payload = sample_fuzzer.generate_fuzzy_payload("MOCK")
    assert "MOCK" in payload


def test_generate_fuzzy_payload_respects_generation(sample_fuzzer: VBAF):
    """Check if the fuzzy payload is always non-empty and a string instance."""
    payload = sample_fuzzer.generate_fuzzy_payload("MOCK")
    assert isinstance(payload, str)
    assert len(payload) > 0


def test_fuzz_runs(sample_fuzzer: VBAF):
    """Check if the fuzzing harness yields and functions as expected."""

    @sample_fuzzer.fuzz(n_attempts=5)
    def mock_infer(request: str):
        return f"ACK: {request[:15]}"

    results = list(mock_infer("MOCK"))
    assert len(results) == 5

    for fuzzy_payload, response in results:
        assert "MOCK" in fuzzy_payload
        assert response.startswith("ACK: ")


def test_invalid_rand_bounds_raises_error():
    """Check if invalid rand_bounds indeed raises an AssertionError."""
    tokens = [str(i) for i in range(3)]
    fuzzer = VBAF(vocabulary=tokens, rand_bounds=(1, 10))
    with pytest.raises(AssertionError):
        fuzzer.generate_fuzzy_payload("MOCK")


def test_invalid_position_bounds_raises_error():
    """Check if invalid position_bounds indeed raises an AssertionError."""
    tokens = [str(i) for i in range(3)]
    fuzzer = VBAF(vocabulary=tokens, position_bounds=(-1, 2))
    with pytest.raises(AssertionError):
        fuzzer.generate_fuzzy_payload("MOCK")


def test_inference_first_arg_is_str(sample_fuzzer: VBAF):
    """Check if the arg of inference is not str, an AssertionError must be raised."""
    with pytest.raises(AssertionError):

        @sample_fuzzer.fuzz()
        def invalid_infer(request: int):
            return request
