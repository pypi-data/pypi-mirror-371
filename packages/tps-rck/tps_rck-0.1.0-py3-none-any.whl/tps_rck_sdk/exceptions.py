#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Custom exceptions for the RCK SDK."""

class RCKException(Exception):
    """Base exception for all rck_sdk errors."""
    pass

class RCKConfigurationError(RCKException):
    """Raised when the SDK is not configured correctly."""
    pass

class RCKAPIError(RCKException):
    """Raised when the RCK API returns an error."""
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self):
        if self.status_code:
            return f"API Error (Status {self.status_code}): {self.args[0]}"
        return f"API Error: {self.args[0]}"
