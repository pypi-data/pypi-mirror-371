#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core RCK API Client.
Handles HTTP requests, rate limiting, concurrency, and response parsing.
"""
import requests
import json
import logging
from typing import Any, Optional, Dict

from .model import RCKConfig, BaseProgram
from .exceptions import RCKAPIError
from ratelimit import sleep_and_retry

logger = logging.getLogger(__name__)

class RCKResponse:
    """Represents a response from the RCK API."""
    def __init__(self, text: str, raw_response: Dict[str, Any]):
        self.text = text
        self.raw = raw_response
        self.success = bool(text or raw_response.get("end_point") is not None)

class RCKClient:
    def __init__(self, config: RCKConfig, sdk_settings: Dict[str, Any]):
        self.config = config
        self.sdk_settings = sdk_settings
        self.semaphore = self.sdk_settings["concurrency_semaphore"]
        limiter = self.sdk_settings["limiter"]
        self.unified_compute = sleep_and_retry(limiter(self._unified_compute_impl))

    def _unified_compute_impl(self, program: BaseProgram, timeout: Optional[float] = None) -> RCKResponse:
        """Executes any RCK program with concurrency control."""
        request_timeout = timeout if timeout is not None else self.sdk_settings["default_timeout"]

        config_payload = program.config.model_dump(exclude_none=True)
        config_payload.pop('api_key', None)
        config_payload.pop('base_url', None)

        program_payload = {
            "start_point": program.start_point.model_dump(exclude_none=True),
            "path": program.get_path_payload()
        }
        
        payload = {
            "config": config_payload,
            "program": program_payload
        }

        headers = {
            "Content-Type": "application/json",
            "topos-api-key": self.config.api_key
        }
        
        logger.debug(f"Acquiring semaphore... (available: {getattr(self.semaphore, '_value', 'N/A')})")
        with self.semaphore:
            logger.debug("Semaphore acquired. Sending POST to /calculs...")
            try:
                resp = requests.post(
                    f"{self.config.base_url}/calculs", 
                    json=payload, 
                    headers=headers, 
                    timeout=request_timeout
                )
                logger.debug(f"Received response: Status={resp.status_code}, Body='{resp.text}'")

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                    except json.JSONDecodeError:
                        raise RCKAPIError(f"Failed to decode JSON response: {resp.text}", resp.status_code, resp.text)
                    
                    end_point = data.get("end_point") or data.get("end_point_raw")
                    
                    if end_point is not None:
                        text = json.dumps(end_point, ensure_ascii=False) if isinstance(end_point, (dict, list)) else str(end_point)
                    else:
                        text = resp.text
                    
                    return RCKResponse(text, data)
                else:
                    raise RCKAPIError(f"API call failed: {resp.text}", resp.status_code, resp.text)

            except requests.exceptions.RequestException as e:
                raise RCKAPIError(f"Network request error: {e}") from e
            finally:
                logger.debug("Semaphore released.")
