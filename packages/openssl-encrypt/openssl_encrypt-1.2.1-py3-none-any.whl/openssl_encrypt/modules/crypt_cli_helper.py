#!/usr/bin/env python3
"""
Cryptography CLI Helper Module

This module provides helper functions for the CLI interface,
particularly for handling extended post-quantum algorithm options.
"""

import logging
from typing import Any, Dict, Optional, Union

# Configure logger
logger = logging.getLogger(__name__)

try:
    from .pqc_adapter import HYBRID_ALGORITHM_MAP, get_default_encryption_data
except ImportError:
    # Fallback if adapter is not available
    def get_default_encryption_data(algorithm: str) -> str:
        """Fallback implementation if adapter is not available"""
        return "aes-gcm"

    HYBRID_ALGORITHM_MAP = {}


def enhance_cli_args(args: Any) -> Any:
    """
    Enhance CLI arguments with better defaults for extended algorithms

    This function modifies the args object in-place to provide better defaults
    for the extended algorithms, while still respecting user choices.

    Args:
        args: The parsed command-line arguments

    Returns:
        The modified args object
    """
    # If no encryption_data is specified, set a default based on algorithm
    if hasattr(args, "algorithm") and hasattr(args, "encryption_data"):
        if args.algorithm and not args.encryption_data:
            # Only set default if user didn't specify a value
            args.encryption_data = get_default_encryption_data(args.algorithm)
            logger.debug(
                f"Using default encryption_data '{args.encryption_data}' for algorithm '{args.algorithm}'"
            )

    return args


def add_extended_algorithm_help(parser: Any) -> None:
    """
    Add extended algorithm help text to the parser

    Args:
        parser: The argparse parser
    """
    # Get the existing help text for the algorithm argument
    if not hasattr(parser, "_actions"):
        return

    for action in parser._actions:
        if action.dest == "algorithm":
            # Add information about the extended algorithms
            original_help = action.help
            extended_help = original_help + "\nExtended algorithms:\n"

            # Add info about HQC algorithms
            extended_help += "  HQC hybrid modes (post-quantum):\n"
            extended_help += "    hqc-128-hybrid, hqc-192-hybrid, hqc-256-hybrid\n"

            # Add info about ML-KEM with ChaCha20
            extended_help += (
                "  ml-kem-512-chacha20: ML-KEM-512 with ChaCha20-Poly1305 (post-quantum)\n"
            )
            extended_help += (
                "  ml-kem-768-chacha20: ML-KEM-768 with ChaCha20-Poly1305 (post-quantum)\n"
            )
            extended_help += (
                "  ml-kem-1024-chacha20: ML-KEM-1024 with ChaCha20-Poly1305 (post-quantum)\n"
            )

            # Update the help text
            action.help = extended_help
            break
