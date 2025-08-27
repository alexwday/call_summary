"""
OAuth connector module for token generation.

This module handles OAuth token generation using client credentials flow
with retry logic, SSL support, and comprehensive error handling.
"""

from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.logging import get_logger
from ..utils.settings import config


def get_oauth_token(execution_id: str, ssl_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Internal function to retrieve OAuth access token using client credentials flow.

    Uses HTTP Basic Authentication to securely send credentials in the
    Authorization header rather than in the request body. Includes retry
    logic with exponential backoff for resilience.

    NOTE: This is an internal function. Use get_authentication() instead.

    Args:
        execution_id: Unique identifier for this execution for logging.
        ssl_config: SSL configuration from workflow setup.

    Returns:
        OAuth token response containing access token and metadata, or None if not configured.

        # Returns: {
        #     "access_token": "eyJhbGciOiJIUzI1NiIs...",
        #     "token_type": "Bearer",
        #     "expires_in": 3600
        # }
        # Or: None if OAuth not configured

    Raises:
        requests.RequestException: If token generation fails after retries.
    """
    logger = get_logger()

    # Check if OAuth is configured - return None if not
    if not config.oauth_endpoint or not config.oauth_client_id or not config.oauth_client_secret:
        logger.debug("OAuth not configured, skipping token generation", execution_id=execution_id)
        return None

    logger.info(
        "Initiating OAuth token generation",
        execution_id=execution_id,
        endpoint=config.oauth_endpoint,
    )

    # Configure session with retry strategy
    session = _create_session_with_retry()

    try:
        # Determine SSL verification setting
        if ssl_config["verify"]:
            verify = ssl_config["cert_path"] if ssl_config["cert_path"] else True
        else:
            verify = False

        # Make OAuth request with Basic Auth
        response = session.post(
            url=config.oauth_endpoint,
            auth=(config.oauth_client_id, config.oauth_client_secret),  # Basic Auth
            data={"grant_type": config.oauth_grant_type},
            verify=verify,
            timeout=30,
        )

        # Check for HTTP errors
        response.raise_for_status()

        # Parse token response
        token_data = response.json()

        # Validate response contains required fields
        if "access_token" not in token_data:
            raise ValueError("OAuth response missing 'access_token' field")

        logger.info(
            "OAuth token generated successfully",
            execution_id=execution_id,
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in", "unknown"),
        )

        return token_data

    except requests.exceptions.HTTPError as e:
        logger.error(
            "OAuth token generation failed with HTTP error",
            execution_id=execution_id,
            status_code=e.response.status_code if e.response else None,
            error=str(e),
        )
        raise

    except requests.exceptions.ConnectionError as e:
        logger.error(
            "OAuth token generation failed - connection error",
            execution_id=execution_id,
            error=str(e),
        )
        raise

    except requests.exceptions.Timeout as e:
        logger.error("OAuth token generation timed out", execution_id=execution_id, error=str(e))
        raise

    except ValueError as e:
        logger.error(
            "Invalid OAuth response format",
            execution_id=execution_id,
            error=str(e),
        )
        raise
    except requests.exceptions.RequestException as e:
        logger.error(
            "Request error during OAuth token generation",
            execution_id=execution_id,
            error=str(e),
        )
        raise

    finally:
        session.close()


def _create_session_with_retry() -> requests.Session:
    """
    Create a requests session with retry configuration.

    Configures exponential backoff retry strategy for resilience against
    temporary network issues and server errors.

    Returns:
        Configured requests.Session with retry adapter.
    """
    session = requests.Session()

    # Configure retry strategy with exponential backoff
    retry_strategy = Retry(
        total=config.oauth_max_retries,
        backoff_factor=config.oauth_retry_delay,  # Exponential backoff multiplier
        status_forcelist=[500, 502, 503, 504],  # Retry on server errors
        allowed_methods=["POST"],  # Only retry POST requests
        raise_on_status=False,  # Don't raise exception on retry
    )

    # Mount retry adapter to session
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def setup_authentication(execution_id: str, ssl_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Setup authentication configuration based on AUTH_METHOD.

    Uses AUTH_METHOD environment variable to determine whether to use
    OAuth or API key authentication. Returns status with success/failure
    similar to SSL setup pattern.

    Args:
        execution_id: Unique identifier for this execution for logging.
        ssl_config: SSL configuration from workflow setup.

    Returns:
        Authentication configuration with status:
        - "success": bool - Whether authentication setup succeeded
        - "method": str - Authentication method (oauth/api_key)
        - "token": str or None - Authentication token if successful
        - "header": dict - Authorization header if successful
        - "error": str or None - Error message if setup failed
        - "decision_details": str - Human-readable description

        # Returns: {"success": True, "method": "oauth", "token": "abc123",
        #          "header": {"Authorization": "Bearer abc123"}, "error": None,
        #          "decision_details": "Authentication method: oauth"}
    """
    logger = get_logger()

    try:
        # Check configured authentication method
        auth_method = config.auth_method

        if auth_method == "oauth":
            result = _handle_oauth_auth(execution_id, ssl_config, logger)
        elif auth_method == "api_key":
            result = _handle_api_key_auth(execution_id, logger)
        else:
            error_msg = f"Invalid AUTH_METHOD: {auth_method}"
            logger.error(error_msg, execution_id=execution_id)
            return {
                "success": False,
                "status": "Failure",
                "method": auth_method,
                "token": None,
                "header": {},
                "error": error_msg,
                "decision_details": f"Authentication failed: {error_msg}",
            }

        # Check if we got a valid token
        if result.get("token") and result["token"] not in [
            "placeholder-token",
            "invalid-auth-method",
        ]:
            return {
                "success": True,
                "status": "Success",
                "method": result["method"],
                "token": result["token"],
                "header": result["header"],
                "error": None,
                "decision_details": f"Authentication method: {result['method']}",
            }

        error_msg = result.get("error", "Failed to obtain authentication token")
        return {
            "success": False,
            "status": "Failure",
            "method": auth_method,
            "token": None,
            "header": {},
            "error": error_msg,
            "decision_details": f"Authentication failed: {error_msg}",
        }

    except Exception as e:  # pylint: disable=broad-exception-caught
        # Must catch all exceptions to ensure auth failures don't crash the workflow.
        # Returns error details for logging while allowing the system to continue.
        error_msg = f"Unexpected error during authentication: {str(e)}"
        logger.error(error_msg, execution_id=execution_id)
        return {
            "success": False,
            "status": "Failure",
            "method": config.auth_method,
            "token": None,
            "header": {},
            "error": error_msg,
            "decision_details": f"Authentication failed: {str(e)}",
        }


def _handle_oauth_auth(execution_id: str, ssl_config: Dict[str, Any], logger) -> Dict[str, Any]:
    """
    Handle OAuth authentication setup.

    Args:
        execution_id: Unique identifier for this execution.
        ssl_config: SSL configuration from workflow.
        logger: Logger instance.

    Returns:
        Authentication configuration dict.
    """
    # Validate OAuth configuration
    if not config.oauth_endpoint or not config.oauth_client_id or not config.oauth_client_secret:
        logger.warning(
            "OAuth selected but credentials not configured - using placeholder",
            execution_id=execution_id,
            endpoint_configured=bool(config.oauth_endpoint),
            client_id_configured=bool(config.oauth_client_id),
            client_secret_configured=bool(config.oauth_client_secret),
        )
        return {
            "method": "placeholder",
            "token": "no-oauth-configured",
            "header": {"Authorization": "Bearer no-oauth-configured"},
        }

    try:
        # Get OAuth token
        oauth_token = get_oauth_token(execution_id, ssl_config)
        if not oauth_token or "access_token" not in oauth_token:
            logger.warning(
                "Failed to obtain OAuth token - using placeholder", execution_id=execution_id
            )
            return {
                "method": "placeholder",
                "token": "oauth-failed",
                "header": {"Authorization": "Bearer oauth-failed"},
            }

        token_type = oauth_token.get("token_type", "Bearer")
        access_token = oauth_token["access_token"]

        logger.info(
            "OAuth authentication configured", execution_id=execution_id, token_type=token_type
        )

        return {
            "method": "oauth",
            "token": access_token,
            "header": {"Authorization": f"{token_type} {access_token}"},
        }

    except (ValueError, requests.exceptions.RequestException) as e:
        error_msg = f"OAuth authentication error: {str(e)}"
        logger.error(error_msg, execution_id=execution_id)
        return {
            "method": "oauth",
            "token": None,
            "header": {},
            "error": error_msg,
        }
    except Exception as e:
        logger.warning(
            "Failed to obtain OAuth token - using placeholder",
            execution_id=execution_id,
            error=str(e),
        )
        return {
            "method": "placeholder",
            "token": "oauth-failed",
            "header": {"Authorization": "Bearer oauth-failed"},
        }


def _handle_api_key_auth(execution_id: str, logger) -> Dict[str, Any]:
    """
    Handle API key authentication setup.

    Args:
        execution_id: Unique identifier for this execution.
        logger: Logger instance.

    Returns:
        Authentication configuration dict.
    """
    # Validate API key configuration
    if not config.api_key:
        error_msg = "API_KEY not configured"
        logger.error(error_msg, execution_id=execution_id)
        return {
            "method": "api_key",
            "token": None,
            "header": {},
            "error": error_msg,
        }

    logger.info("API key authentication configured", execution_id=execution_id)

    return {
        "method": "api_key",
        "token": config.api_key,
        "header": {"Authorization": f"Bearer {config.api_key}"},
    }
