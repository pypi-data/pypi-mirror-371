"""Validation and query param helpers for Astral MCP server."""

from __future__ import annotations

import re
from typing import Dict, Optional, Union

# Shared constants
ERROR_TEXT_TRUNCATE_LENGTH = 500
MIN_QUERY_LIMIT = 1
MAX_QUERY_LIMIT = 100


def validate_query_args(
    limit: Optional[int],
    offset: Optional[int],
    prover: Optional[str],
) -> None:
    if limit is not None and (
        not isinstance(limit, int) or limit < MIN_QUERY_LIMIT or limit > MAX_QUERY_LIMIT
    ):
        raise ValueError(
            f"limit must be an integer between {MIN_QUERY_LIMIT} and {MAX_QUERY_LIMIT}"
        )
    if offset is not None and (not isinstance(offset, int) or offset < 0):
        raise ValueError("offset must be a non-negative integer")
    if prover is not None and not re.match(r"^0x[a-fA-F0-9]{40}$", prover):
        raise ValueError(
            "prover must be a valid 40-character hexadecimal address starting with 0x"
        )


def build_query_params(
    chain: Optional[str],
    prover: Optional[str],
    limit: Optional[int],
    offset: Optional[int],
) -> Dict[str, Union[str, int]]:
    params: Dict[str, Union[str, int]] = {}
    if chain is not None:
        params["chain"] = chain
    if prover is not None:
        params["prover"] = prover
    if limit is not None:
        params["limit"] = limit
    if offset is not None:
        params["offset"] = offset
    return params
