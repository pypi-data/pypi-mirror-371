"""
Astral MCP Server

A FastMCP-based server that provides tools for querying location attestations through the Astral API.
"""

import logging
import re
from typing import Dict, Optional

import httpx
from mcp.server.fastmcp import FastMCP

from astral_mcp_server.helpers import (
    ERROR_TEXT_TRUNCATE_LENGTH,
    build_query_params,
    extract_location_proofs_list,
    extract_pagination,
    feature_collection_from_attestations,
    geojson_blocks_for_single,
    validate_query_args,
)

# Import from absolute paths when running as script
try:
    from .config import (
        ASTRAL_CONFIG_ENDPOINT,
        ASTRAL_HEALTH_ENDPOINT,
        ASTRAL_LOCATION_PROOFS_ENDPOINT,
        DEFAULT_TIMEOUT,
        SERVER_NAME,
        SERVER_VERSION,
        get_api_key,
    )
except ImportError:  # pragma: no cover
    # Fallback for when running as script
    from config import (  # type: ignore
        ASTRAL_CONFIG_ENDPOINT,
        ASTRAL_HEALTH_ENDPOINT,
        ASTRAL_LOCATION_PROOFS_ENDPOINT,
        DEFAULT_TIMEOUT,
        SERVER_NAME,
        SERVER_VERSION,
        get_api_key,
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP app
app = FastMCP(SERVER_NAME)


@app.tool()
async def check_astral_api_health() -> Dict[str, object]:
    """
    Check the health status of the Astral API.

    Performs a health check against the Astral API endpoint to verify connectivity and service availability.

    Returns:
        Dict[str, Any]: Health check response containing status information

    Raises:
        Exception: If the health check fails or times out
    """
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            logger.info(f"Checking Astral API health at: {ASTRAL_HEALTH_ENDPOINT}")
            response = await client.get(ASTRAL_HEALTH_ENDPOINT)
            response.raise_for_status()

            health_data = response.json()

            result = {
                "status": "healthy",
                "endpoint": ASTRAL_HEALTH_ENDPOINT,
                "response_code": response.status_code,
                "response_time_ms": (
                    int(response.elapsed.total_seconds() * 1000)
                    if response.elapsed is not None
                    else None
                ),
                "api_data": health_data,
            }

            logger.info(f"Health check successful: {result['status']}")
            return result

    except httpx.TimeoutException as exc:
        error_msg = f"Health check timed out after {DEFAULT_TIMEOUT} seconds"
        logger.error(error_msg)
        raise Exception(error_msg) from exc

    except httpx.HTTPStatusError as exc:
        error_msg = (
            "Health check failed with status "
            f"{exc.response.status_code}: {exc.response.text}"
        )
        logger.error(error_msg)
        raise Exception(error_msg) from exc

    except Exception as exc:  # pragma: no cover
        error_msg = f"Health check failed: {exc!s}"
        logger.error(error_msg)
        raise Exception(error_msg) from exc


@app.tool()
async def get_server_info() -> Dict[str, object]:
    """
    Get information about this MCP server.

    Returns basic metadata and configuration information about the
    Astral MCP server instance.

    Returns:
        Dict[str, Any]: Server information including name, version, and capabilities
    """
    api_key_configured = get_api_key() is not None

    return {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "description": "MCP server for querying Astral location attestations",
        "api_key_configured": api_key_configured,
        "astral_health_endpoint": ASTRAL_HEALTH_ENDPOINT,
        "capabilities": [
            "health_check",
            "server_info",
            "query_location_proofs",
            "get_location_proof_by_uid",
            "get_astral_config",
        ],
    }


@app.tool()
async def query_location_proofs(
    chain: Optional[str] = None,
    prover: Optional[str] = None,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    geojson_block: bool = False,
) -> object:
    """
    Query location proofs (attestations) from the Astral API with filtering capabilities.

    Enables searching for location attestations using chain, prover, and limit filters to analyze blockchain
    location activity and identify patterns in attestation data.

    Args:
        chain (Optional[str]): Filter by blockchain network (e.g., "ethereum", "polygon").
        prover (Optional[str]): Filter by prover address (hexadecimal address).
        limit (Optional[int]): Max results to return (default: 10, max: 100).
        offset (Optional[int]): Results to skip for pagination (default: 0).
        geojson_block (bool): When True, append a separate JSON block containing a GeoJSON FeatureCollection.

    Returns:
        object: The standard result dict, or when geojson_block=True, a list of two JSON content blocks.

    Raises:
        Exception: If the API request fails or parameters are invalid.
    """
    try:
        validate_query_args(limit, offset, prover)
        params = build_query_params(chain, prover, limit, offset)

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            logger.info(f"Querying location proofs with params: {params}")

            response = await client.get(ASTRAL_LOCATION_PROOFS_ENDPOINT, params=params)
            response.raise_for_status()

            data = response.json()

            # Extract and flatten location proofs into a list of dicts
            location_proofs = extract_location_proofs_list(data)
            pagination = extract_pagination(data)

            count = len(location_proofs)
            logger.info(f"Successfully retrieved {count} location proofs")

            result: Dict[str, object] = {
                "success": True,
                "data": location_proofs,
                "query_params": params,
                "response_code": response.status_code,
                "response_time_ms": (
                    int(response.elapsed.total_seconds() * 1000)
                    if response.elapsed is not None
                    else None
                ),
            }
            if pagination is not None:
                result["pagination"] = pagination

            if geojson_block:
                fc = feature_collection_from_attestations(location_proofs)
                return [
                    {"type": "json", "data": result},
                    {"type": "json", "data": fc},
                ]

            return result

    except ValueError as e:
        error_msg = f"Invalid parameter: {e!s}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "validation_error",
            "message": error_msg,
            "details": {"parameter_validation": f"{e!s}"},
        }

    except httpx.TimeoutException:
        error_msg = f"Request timed out after {DEFAULT_TIMEOUT} seconds"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "timeout_error",
            "message": error_msg,
            "details": {"timeout_seconds": DEFAULT_TIMEOUT},
        }

    except httpx.HTTPStatusError as e:
        error_msg = f"API request failed with status {e.response.status_code}"
        logger.error(f"{error_msg}: {e.response.text}")
        return {
            "success": False,
            "error": "api_error",
            "message": error_msg,
            "details": {
                "status_code": e.response.status_code,
                "response_text": e.response.text[:ERROR_TEXT_TRUNCATE_LENGTH],
            },
        }

    except Exception as e:  # pragma: no cover
        error_msg = f"Unexpected error querying location proofs: {e!s}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "unexpected_error",
            "message": error_msg,
            "details": {"exception_type": type(e).__name__},
        }


@app.tool()
async def get_location_proof_by_uid(uid: str, geojson_block: bool = False) -> object:
    """
    Retrieve a specific location proof attestation by its unique identifier.

    Enables fetching complete attestation details including raw content, decoded fields, and verification evidence for analysis.

    Args:
        uid (str): 66-character hex string starting with 0x.
        geojson_block (bool): When True, append a separate JSON block containing a GeoJSON FeatureCollection.

    Returns:
        object: The standard result dict, or when geojson_block=True, a list of two JSON content blocks.

    Raises:
        Exception: If the UID format is invalid or API request fails.
    """
    try:
        if not isinstance(uid, str) or not re.match(r"^0x[a-fA-F0-9]{64}$", uid):
            raise ValueError(
                "uid must be a 66-character hexadecimal string starting with 0x"
            )
        endpoint = f"{ASTRAL_LOCATION_PROOFS_ENDPOINT}/{uid}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            logger.info(f"Fetching location proof with UID: {uid}")
            response = await client.get(endpoint)
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"Location proof not found for UID: {uid}",
                    "details": {"attempted_uid": uid},
                }
            response.raise_for_status()
            data = response.json()
            result: Dict[str, object] = {
                "success": True,
                "data": data,
                "uid": uid,
                "response_code": response.status_code,
                "response_time_ms": (
                    int(response.elapsed.total_seconds() * 1000)
                    if response.elapsed is not None
                    else None
                ),
            }
            logger.info(f"Successfully retrieved location proof for UID: {uid}")
            return geojson_blocks_for_single(data, result) if geojson_block else result
    except ValueError as e:
        error_msg = f"Invalid UID format: {e!s}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "validation_error",
            "message": error_msg,
            "details": {
                "attempted_uid": uid,
                "format_requirement": "66-character hex string starting with 0x",
            },
        }
    except httpx.TimeoutException:
        error_msg = f"Request timed out after {DEFAULT_TIMEOUT} seconds"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "timeout_error",
            "message": error_msg,
            "details": {"attempted_uid": uid, "timeout_seconds": DEFAULT_TIMEOUT},
        }
    except httpx.HTTPStatusError as e:
        error_msg = f"API request failed with status {e.response.status_code}"
        logger.error(f"{error_msg}: {e.response.text}")
        return {
            "success": False,
            "error": "api_error",
            "message": error_msg,
            "details": {
                "attempted_uid": uid,
                "status_code": e.response.status_code,
                "response_text": e.response.text[:ERROR_TEXT_TRUNCATE_LENGTH],
            },
        }
    except Exception as e:  # pragma: no cover
        error_msg = f"Unexpected error fetching location proof: {e!s}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "unexpected_error",
            "message": error_msg,
            "details": {"attempted_uid": uid, "exception_type": type(e).__name__},
        }


@app.tool()
async def get_astral_config() -> Dict[str, object]:
    """
    Get Astral API configuration information including supported chains and schemas.

    Provides configuration data to help users understand which chains, schemas, and capabilities are supported
        by the Astral API for making informed queries.

    Returns:
        Dict[str, Any]: Configuration data including chains, schemas, and API capabilities

    Raises:
        Exception: If the configuration endpoint is unavailable
    """
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            logger.info(
                f"Fetching Astral API configuration from: {ASTRAL_CONFIG_ENDPOINT}"
            )

            response = await client.get(ASTRAL_CONFIG_ENDPOINT)
            response.raise_for_status()

            config_data = response.json()

            result = {
                "success": True,
                "data": config_data,
                "endpoint": ASTRAL_CONFIG_ENDPOINT,
                "response_code": response.status_code,
                "response_time_ms": (
                    int(response.elapsed.total_seconds() * 1000)
                    if response.elapsed is not None
                    else None
                ),
            }

            logger.info("Successfully retrieved Astral API configuration")
            return result

    except httpx.TimeoutException:
        error_msg = f"Configuration request timed out after {DEFAULT_TIMEOUT} seconds"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "timeout_error",
            "message": error_msg,
            "details": {"timeout_seconds": DEFAULT_TIMEOUT},
        }

    except httpx.HTTPStatusError as e:
        error_msg = f"Configuration request failed with status {e.response.status_code}"
        logger.error(f"{error_msg}: {e.response.text}")
        return {
            "success": False,
            "error": "api_error",
            "message": error_msg,
            "details": {
                "status_code": e.response.status_code,
                "response_text": e.response.text[:ERROR_TEXT_TRUNCATE_LENGTH],
            },
        }

    except Exception as e:  # pragma: no cover
        error_msg = f"Unexpected error fetching configuration: {e!s}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": "unexpected_error",
            "message": error_msg,
            "details": {"exception_type": type(e).__name__},
        }


def main() -> None:
    """
    Main entry point for running the MCP server.

    This function starts the FastMCP server and handles the event loop.
    """
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")

    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:  # pragma: no cover
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
