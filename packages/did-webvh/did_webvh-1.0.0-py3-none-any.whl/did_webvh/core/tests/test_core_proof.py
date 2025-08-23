import pytest

from did_webvh.askar import AskarSigningKey
from did_webvh.core.proof import (
    di_jcs_sign,
    di_jcs_verify,
)
from did_webvh.core.state import DocumentState


def test_jcs_sign():
    proof_input = DocumentState.initial(
        params={
            "updateKeys": ["z6MkrPW2qVDWmgrGn7j7G6SRKSzzkLuujC8oV9wMUzSPQoL4"],
        },
        document={
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": "did:tdw:{SCID}:domain.example\n",
        },
    ).history_line()
    sk1 = AskarSigningKey.generate("ed25519")
    proof = di_jcs_sign(
        proof_input,
        sk=sk1,
        purpose="assertionMethod",
        challenge="challenge",
    )
    assert isinstance(proof, dict)
    di_jcs_verify(proof_input, proof, sk1)
    # test key loading from verification method
    di_jcs_verify(proof_input, proof, sk1.get_verification_method())

    sk2 = AskarSigningKey.generate("p256")
    proof = di_jcs_sign(
        proof_input,
        sk=sk2,
        purpose="assertionMethod",
        challenge="challenge",
    )
    di_jcs_verify(proof_input, proof, sk2)

    with pytest.raises(ValueError):
        # test incorrect key
        di_jcs_verify(proof_input, proof, sk1)

    sk3 = AskarSigningKey.generate("p384")
    proof = di_jcs_sign(
        proof_input,
        sk=sk3,
        purpose="assertionMethod",
        challenge="challenge",
    )
    di_jcs_verify(proof_input, proof, sk3)

    with pytest.raises(TypeError):
        # test unsupported key type
        _ = di_jcs_sign(
            proof_input,
            sk=AskarSigningKey.generate("bls12381g1g2"),
            purpose="assertionMethod",
            challenge="challenge",
        )
