"""Update existing did:webvh DIDs."""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Union

import aries_askar

from .askar import AskarSigningKey
from .const import ASKAR_STORE_FILENAME, DOCUMENT_FILENAME, HISTORY_FILENAME
from .core.state import DocumentState
from .core.types import SigningKey
from .history import load_local_history


async def auto_update_did(
    doc_dir: Path,
    pass_key: str,
    *,
    check_modified: bool = True,
    params_update: dict = None,
    timestamp: Union[datetime, str] = None,
) -> DocumentState:
    """Automatically update a history log."""
    doc_path = doc_dir.joinpath(DOCUMENT_FILENAME)
    if not doc_path.is_file():
        raise ValueError(f"Document file ({DOCUMENT_FILENAME}) not found")
    with open(doc_path) as docf:
        document = json.load(docf)
    history_path = doc_dir.joinpath(HISTORY_FILENAME)
    prev_state, _ = await load_local_history(history_path)
    store = await aries_askar.Store.open(
        f"sqlite://{doc_dir}/{ASKAR_STORE_FILENAME}", pass_key=pass_key
    )
    sk = None
    async with store.session() as session:
        for kid in prev_state.update_keys:
            found = await session.fetch_key(kid)
            if found:
                # FIXME check public key matches?
                sk = AskarSigningKey(found.key, kid=kid)
    if not sk:
        raise ValueError("No applicable signing key found")
    return await update_did(
        prev_state,
        document,
        history_path,
        sk,
        check_modified=check_modified,
        params_update=params_update,
        timestamp=timestamp,
    )


async def update_did(
    prev_state: DocumentState,
    document: Union[str, dict],
    history_path: Path,
    sk: SigningKey,
    *,
    check_modified: bool,
    params_update: dict = None,
    timestamp: Union[datetime, str] = None,
) -> DocumentState:
    """Update a history log, given a new document state and signing key."""
    state = prev_state.create_next(
        document, params_update=params_update, timestamp=timestamp
    )
    if (
        check_modified
        and state.document == prev_state.document
        and state.params == prev_state.params
    ):
        raise ValueError("There are no document or parameter updates to apply")
    # FIXME check that the signing key is present in the updateKeys
    state.proofs.append(state.create_proof(sk, timestamp=state.timestamp))
    with open(history_path, "a") as out:
        print(
            json.dumps(state.history_line()),
            file=out,
        )
    return state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="update a did:webvh DID")
    parser.add_argument("did", help="the DID to update")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="automatically update the DID using a local Askar store",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="perform an update even if no changes are detected",
    )
    args = parser.parse_args()

    if not args.auto:
        raise SystemExit("Only automatic updating (--auto) is currently supported")

    doc_dir = Path(args.did)
    if not doc_dir or not doc_dir.is_dir():
        raise SystemExit("Document directory not found")

    try:
        state = asyncio.run(
            auto_update_did(doc_dir, "password", check_modified=not args.force)
        )
    except ValueError as err:
        raise SystemExit(f"Update failed: {err}") from None

    doc_path = doc_dir.joinpath(DOCUMENT_FILENAME)
    with open(doc_path, "w") as out:
        print(
            json.dumps(state.document, indent=2),
            file=out,
        )
    print("Updated DID in", doc_dir)
