"""Provisioning of new did:webvh DIDs."""

import argparse
import asyncio
import base64
import json
import re
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Optional, Union

import aries_askar
import jsoncanon

from .askar import AskarSigningKey
from .const import (
    ASKAR_STORE_FILENAME,
    DOCUMENT_FILENAME,
    HISTORY_FILENAME,
    METHOD_NAME,
    METHOD_VERSION,
)
from .core.hash_utils import DEFAULT_HASH, HashInfo
from .core.proof import VerifyingKey
from .core.state import DocumentState
from .domain_path import DomainPath
from .history import load_local_history, write_document_state

DID_CONTEXT = "https://www.w3.org/ns/did/v1"
DOMAIN_PATTERN = re.compile(r"^([a-zA-Z0-9%_\-]+\.)+[a-zA-Z0-9%_\.\-]{2,}$")


async def auto_provision_did(
    domain_path: str,
    key_alg: str,
    pass_key: str,
    *,
    prerotation: bool = False,
    extra_params: dict | None = None,
    hash_name: str | None = None,
    target_dir: str | Path | None = None,
) -> tuple[Path, DocumentState, AskarSigningKey]:
    """Automatically provision a new did:webvh DID.

    This will create a new Askar store for key management.
    """
    pathinfo = DomainPath.parse_normalized(domain_path)
    update_key = AskarSigningKey.generate(key_alg)
    placeholder_id = f"did:{METHOD_NAME}:{pathinfo.identifier}"
    genesis = genesis_document(placeholder_id)
    params = deepcopy(extra_params) if extra_params else {}
    params["updateKeys"] = [update_key.multikey]
    if prerotation:
        next_key = AskarSigningKey.generate(key_alg)
        hash_info = HashInfo.from_name(hash_name or DEFAULT_HASH)
        next_key_hash = hash_info.formatted_hash(next_key.multikey.encode("utf-8"))
        params["nextKeyHashes"] = [next_key_hash]
    else:
        next_key = None
        next_key_hash = None
    state = provision_did(genesis, params=params, hash_name=hash_name)
    doc_dir = Path(target_dir) if target_dir else Path(f"{pathinfo.domain}_{state.scid}")
    doc_dir.mkdir(exist_ok=bool(target_dir))

    store = await aries_askar.Store.provision(
        f"sqlite://{doc_dir}/{ASKAR_STORE_FILENAME}", pass_key=pass_key
    )
    async with store.session() as session:
        await session.insert_key(update_key.kid, update_key.key)
        if next_key:
            await session.insert_key(
                next_key.kid, next_key.key, tags={"hash": next_key_hash}
            )
    await store.close()

    state.proofs.append(
        state.create_proof(
            update_key,
            timestamp=state.timestamp,
        )
    )
    write_document_state(doc_dir, state)

    # verify log
    await load_local_history(doc_dir.joinpath(HISTORY_FILENAME), verify_proofs=True)

    return (doc_dir, state, update_key)


def encode_verification_method(vk: VerifyingKey, controller: str = None) -> dict:
    """Format a verifiying key as a DID Document verification method."""
    keydef = {
        "type": "Multikey",
        "publicKeyMultibase": vk.multikey,
    }
    kid = vk.kid
    if not kid:
        kid = "#" + (
            base64.urlsafe_b64encode(sha256(jsoncanon.canonicalize(keydef)).digest())
            .decode("ascii")
            .rstrip("=")
        )
    fpos = kid.find("#")
    if fpos < 0:
        raise RuntimeError("Missing fragment in verification method ID")
    elif fpos > 0:
        controller = kid[:fpos]
    else:
        controller = controller or ""
        kid = controller + kid
    return {"id": kid, "controller": controller, **keydef}


def genesis_document(placeholder_id: str) -> dict:
    """Generate a standard genesis document from a set of verification keys.

    The exact format of this document may change over time.
    """
    # FIXME check format of placeholder ID
    return {
        "@context": [DID_CONTEXT],
        "id": placeholder_id,
    }


def provision_did(
    document: Union[str, dict],
    *,
    params: Optional[dict] = None,
    timestamp: Optional[datetime] = None,
    hash_name: Optional[str] = None,
) -> DocumentState:
    """Provision a new DID from an initial document state.

    This does not create a new history file or add proof(s) to the state.
    """
    if not params:
        params = {}
    method = f"did:{METHOD_NAME}:{METHOD_VERSION}"
    if "method" in params and params["method"] != method:
        raise ValueError("Cannot override 'method' parameter")
    params["method"] = method
    return DocumentState.initial(
        params=params, document=document, timestamp=timestamp, hash_name=hash_name
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="provision a new did:webvh DID")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="automatically provision a new key using a local Askar store",
    )
    parser.add_argument(
        "--algorithm",
        help="the signing key algorithm (default ed25519)",
    )
    parser.add_argument("--hash", help="the name of the hash function (default sha-256)")
    parser.add_argument(
        "domain_path", help="the domain name and optional path components"
    )
    args = parser.parse_args()

    if not args.auto:
        raise SystemExit("Only automatic provisioning (--auto) is currently supported")

    try:
        doc_dir, state, _ = asyncio.run(
            auto_provision_did(
                args.domain_path,
                args.algorithm or "ed25519",
                "password",
                hash_name=args.hash,
            )
        )
    except ValueError as err:
        raise SystemExit(f"Provisioning failed: {err}") from None

    doc_path = doc_dir.joinpath(DOCUMENT_FILENAME)
    with open(doc_path, "w") as out:
        print(
            json.dumps(state.document, indent=2),
            file=out,
        )
    print("Provisioned DID in", doc_dir)
