#!/usr/bin/env python3
"""
Subparser implementation for crypt_cli to provide command-specific help.
This module patches the main function to use subparsers.
"""

import argparse

from .crypt_cli_helper import add_extended_algorithm_help
from .crypt_core import EncryptionAlgorithm


def setup_encrypt_parser(subparser):
    """Set up arguments specific to the encrypt command"""
    # Get all available algorithms, marking deprecated ones
    all_algorithms = [algo.value for algo in EncryptionAlgorithm]

    # Build help text with deprecated warnings
    algorithm_help_text = "Encryption algorithm to use:\n"
    for algo in sorted(all_algorithms):
        if algo == EncryptionAlgorithm.FERNET.value:
            description = "default, AES-128-CBC with authentication"
        elif algo == EncryptionAlgorithm.AES_GCM.value:
            description = "AES-256 in GCM mode, high security, widely trusted"
        elif algo == EncryptionAlgorithm.AES_GCM_SIV.value:
            description = "AES-256 in GCM-SIV mode, resistant to nonce reuse"
        elif algo == EncryptionAlgorithm.AES_OCB3.value:
            description = "AES-256 in OCB3 mode, faster than GCM (DEPRECATED)"
        elif algo == EncryptionAlgorithm.AES_SIV.value:
            description = "AES in SIV mode, synthetic IV"
        elif algo == EncryptionAlgorithm.CHACHA20_POLY1305.value:
            description = "modern AEAD cipher with 12-byte nonce"
        elif algo == EncryptionAlgorithm.XCHACHA20_POLY1305.value:
            description = "ChaCha20-Poly1305 with 24-byte nonce, safer for high-volume encryption"
        elif algo == EncryptionAlgorithm.CAMELLIA.value:
            description = "Camellia in CBC mode (DEPRECATED)"
        elif algo == EncryptionAlgorithm.ML_KEM_512_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 1 (NIST FIPS 203)"
        elif algo == EncryptionAlgorithm.ML_KEM_768_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 3 (NIST FIPS 203)"
        elif algo == EncryptionAlgorithm.ML_KEM_1024_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 5 (NIST FIPS 203)"
        elif algo == EncryptionAlgorithm.KYBER512_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 1 (DEPRECATED - use ml-kem-512-hybrid)"
        elif algo == EncryptionAlgorithm.KYBER768_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 3 (DEPRECATED - use ml-kem-768-hybrid)"
        elif algo == EncryptionAlgorithm.KYBER1024_HYBRID.value:
            description = "post-quantum key exchange with AES-256-GCM, NIST level 5 (DEPRECATED - use ml-kem-1024-hybrid)"
        elif algo == "mayo-1-hybrid":
            description = "MAYO-1 multivariate hybrid mode (post-quantum signature)"
        elif algo == "mayo-3-hybrid":
            description = "MAYO-3 multivariate hybrid mode (post-quantum signature)"
        elif algo == "mayo-5-hybrid":
            description = "MAYO-5 multivariate hybrid mode (post-quantum signature)"
        elif algo == "cross-128-hybrid":
            description = "CROSS-128 code-based hybrid mode (post-quantum signature)"
        elif algo == "cross-192-hybrid":
            description = "CROSS-192 code-based hybrid mode (post-quantum signature)"
        elif algo == "cross-256-hybrid":
            description = "CROSS-256 code-based hybrid mode (post-quantum signature)"
        else:
            description = "encryption algorithm"
        algorithm_help_text += f"  {algo}: {description}\n"

    subparser.add_argument(
        "--algorithm",
        type=str,
        choices=all_algorithms,
        default=EncryptionAlgorithm.FERNET.value,
        help=algorithm_help_text,
    )

    # Add extended algorithm help
    add_extended_algorithm_help(subparser)

    # Template selection group
    template_group = subparser.add_mutually_exclusive_group()
    template_group.add_argument(
        "--quick", action="store_true", help="Use quick but secure configuration"
    )
    template_group.add_argument(
        "--standard",
        action="store_true",
        help="Use standard security configuration (default)",
    )
    template_group.add_argument(
        "--paranoid", action="store_true", help="Use maximum security configuration"
    )

    # Add template argument
    subparser.add_argument(
        "-t",
        "--template",
        help="Specify a template name (built-in or from ./template directory)",
    )

    # Password options
    subparser.add_argument(
        "--password",
        "-p",
        help="Password (will prompt if not provided, or use CRYPT_PASSWORD environment variable)",
    )
    subparser.add_argument(
        "--random",
        type=int,
        metavar="LENGTH",
        help="Generate a random password of specified length for encryption",
    )

    # I/O options
    subparser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input file to encrypt",
    )
    subparser.add_argument("--output", "-o", help="Output file (optional)")
    subparser.add_argument(
        "--overwrite",
        "-f",
        action="store_true",
        help="Overwrite the input file with the output",
    )
    subparser.add_argument(
        "--shred",
        "-s",
        action="store_true",
        help="Securely delete the original file after encryption",
    )
    subparser.add_argument(
        "--shred-passes",
        type=int,
        default=3,
        help="Number of passes for secure deletion (default: 3)",
    )

    # Advanced encryption options
    hash_group = subparser.add_argument_group("Hash options")

    # Add global KDF rounds parameter
    hash_group.add_argument(
        "--kdf-rounds",
        type=int,
        default=0,
        help="Default number of rounds for all KDFs when enabled without specific rounds (overrides the default of 10)",
    )

    # SHA family arguments - updated to match the main CLI
    hash_group.add_argument(
        "--sha512-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA-512 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha384-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA-384 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha256-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA-256 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha224-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA-224 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha3-256-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA3-256 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha3-512-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA3-512 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha3-384-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA3-384 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--sha3-224-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHA3-224 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--blake2b-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of BLAKE2b iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--blake3-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of BLAKE3 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--shake256-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHAKE-256 iterations (default: 1,000,000 if flag provided without value)",
    )
    hash_group.add_argument(
        "--shake128-rounds",
        type=int,
        nargs="?",
        const=1,
        default=0,
        help="Number of SHAKE-128 iterations (default: 1,000,000 if flag provided without value)",
    )


    # Scrypt options for encryption
    scrypt_group = subparser.add_argument_group("Scrypt options")
    scrypt_group.add_argument(
        "--enable-scrypt",
        action="store_true",
        help="Use Scrypt password hashing (requires scrypt package)",
        default=False,
    )
    scrypt_group.add_argument(
        "--scrypt-rounds",
        type=int,
        default=0,
        help="Use scrypt rounds for iterating (default when enabled: 10)",
    )
    scrypt_group.add_argument(
        "--scrypt-n",
        type=int,
        default=128,
        help="Scrypt CPU/memory cost factor N (default: 0, not used. Use power of 2 like 16384)",
    )
    scrypt_group.add_argument(
        "--scrypt-r", type=int, default=8, help="Scrypt block size parameter r (default: 8)"
    )
    scrypt_group.add_argument(
        "--scrypt-p", type=int, default=1, help="Scrypt parallelization parameter p (default: 1)"
    )

    # Argon2 options for encryption
    argon2_group = subparser.add_argument_group("Argon2 options")
    argon2_group.add_argument(
        "--enable-argon2",
        action="store_true",
        help="Use Argon2 password hashing (requires argon2-cffi package)",
        default=False,
    )
    argon2_group.add_argument(
        "--argon2-rounds",
        type=int,
        default=0,
        help="Argon2 time cost parameter (default when enabled: 10)",
    )
    argon2_group.add_argument(
        "--argon2-time",
        type=int,
        default=3,
        help="Argon2 time cost parameter (default: 3)",
    )
    argon2_group.add_argument(
        "--argon2-memory",
        type=int,
        default=65536,
        help="Argon2 memory cost in KB (default: 65536 - 64MB)",
    )
    argon2_group.add_argument(
        "--argon2-parallelism",
        type=int,
        default=4,
        help="Argon2 parallelism factor (default: 4)",
    )
    argon2_group.add_argument(
        "--argon2-hash-len",
        type=int,
        default=32,
        help="Argon2 hash length in bytes (default: 32)",
    )
    argon2_group.add_argument(
        "--argon2-type",
        type=int,
        default=2,
        help="Argon2 algorithm type: 0=Argon2d, 1=Argon2i, 2=Argon2id (default: 2)",
    )

    # Balloon hashing options for encryption
    balloon_group = subparser.add_argument_group("Balloon Hashing options")
    balloon_group.add_argument(
        "--enable-balloon",
        action="store_true",
        help="Enable Balloon Hashing KDF",
    )
    balloon_group.add_argument(
        "--balloon-time-cost",
        type=int,
        default=3,
        help="Time cost parameter for Balloon hashing - controls computational complexity. Higher values increase security but also processing time.",
    )
    balloon_group.add_argument(
        "--balloon-space-cost",
        type=int,
        default=65536,
        help="Space cost parameter for Balloon hashing in bytes - controls memory usage. Higher values increase security but require more memory.",
    )
    balloon_group.add_argument(
        "--balloon-parallelism",
        type=int,
        default=4,
        help="Parallelism parameter for Balloon hashing - controls number of parallel threads. Higher values can improve performance on multi-core systems.",
    )
    balloon_group.add_argument(
        "--balloon-rounds",
        type=int,
        default=0,
        help="Number of rounds for Balloon hashing (default when enabled: 10). More rounds increase security but also processing time.",
    )
    balloon_group.add_argument(
        "--balloon-hash-len",
        type=int,
        default=32,
        help="Length of the final hash output in bytes for Balloon hashing.",
    )

    # HKDF options for encryption
    hkdf_group = subparser.add_argument_group("HKDF options")
    hkdf_group.add_argument(
        "--enable-hkdf",
        action="store_true",
        help="Enable HKDF key derivation",
        default=False,
    )
    hkdf_group.add_argument(
        "--hkdf-rounds",
        type=int,
        default=1,
        help="Number of HKDF chained rounds (default: 1)",
    )
    hkdf_group.add_argument(
        "--hkdf-algorithm",
        choices=["sha224", "sha256", "sha384", "sha512"],
        default="sha256",
        help="Hash algorithm for HKDF (default: sha256)",
    )
    hkdf_group.add_argument(
        "--hkdf-info",
        type=str,
        default="openssl_encrypt_hkdf",
        help="HKDF info string for context (default: openssl_encrypt_hkdf)",
    )

    # PQC options for encryption
    pqc_group = subparser.add_argument_group("Post-Quantum Cryptography options")
    pqc_group.add_argument("--pqc-keyfile", help="Path to save/load the PQC key file")
    pqc_group.add_argument(
        "--pqc-store-key",
        action="store_true",
        help="Store the PQC private key in the encrypted file",
    )

    # Keystore options
    keystore_group = subparser.add_argument_group("Keystore options")
    keystore_group.add_argument(
        "--keystore-path",
        help="Path to the keystore file for PQC keys",
    )
    keystore_group.add_argument(
        "--keystore-password",
        help="Password for the keystore (will prompt if not provided)",
    )
    keystore_group.add_argument(
        "--dual-encrypt-key",
        help="PQC key identifier for dual encryption",
    )
    keystore_group.add_argument(
        "--encryption-data",
        help="Additional data to be encrypted alongside the file",
    )


def setup_decrypt_parser(subparser):
    """Set up arguments specific to the decrypt command"""
    # Password options
    subparser.add_argument(
        "--password",
        "-p",
        help="Password (will prompt if not provided, or use CRYPT_PASSWORD environment variable)",
    )

    # I/O options
    subparser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input file to decrypt",
    )
    subparser.add_argument("--output", "-o", help="Output file (optional)")
    subparser.add_argument(
        "--overwrite",
        "-f",
        action="store_true",
        help="Overwrite the input file with the output",
    )
    subparser.add_argument(
        "--shred",
        "-s",
        action="store_true",
        help="Securely delete the original file after decryption",
    )
    subparser.add_argument(
        "--shred-passes",
        type=int,
        default=3,
        help="Number of passes for secure deletion (default: 3)",
    )

    # PQC options for decryption
    pqc_group = subparser.add_argument_group("Post-Quantum Cryptography options")
    pqc_group.add_argument("--pqc-keyfile", help="Path to load the PQC key file for decryption")

    # Keystore options for decryption
    keystore_group = subparser.add_argument_group("Keystore options")
    keystore_group.add_argument(
        "--keystore-path",
        help="Path to the keystore file for PQC keys",
    )
    keystore_group.add_argument(
        "--keystore-password",
        help="Password for the keystore (will prompt if not provided)",
    )


def setup_shred_parser(subparser):
    """Set up arguments specific to the shred command"""
    subparser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input file or directory to shred (supports glob patterns)",
    )
    subparser.add_argument(
        "--shred-passes",
        type=int,
        default=3,
        help="Number of passes for secure deletion (default: 3)",
    )
    subparser.add_argument(
        "--recursive",
        "-r",
        action="store_true",
        help="Process directories recursively when shredding",
    )


def setup_generate_password_parser(subparser):
    """Set up arguments specific to the generate-password command"""
    subparser.add_argument(
        "length",
        type=int,
        nargs="?",
        default=32,
        help="Password length (default: 32)",
    )
    subparser.add_argument(
        "--use-lowercase",
        action="store_true",
        help="Include lowercase letters",
    )
    subparser.add_argument(
        "--use-uppercase",
        action="store_true",
        help="Include uppercase letters",
    )
    subparser.add_argument(
        "--use-digits",
        action="store_true",
        help="Include digits",
    )
    subparser.add_argument(
        "--use-special",
        action="store_true",
        help="Include special characters",
    )


def setup_simple_parser(subparser):
    """Set up arguments for simple commands (security-info, check-argon2, check-pqc, version)"""
    # These commands don't need any special arguments
    pass


def create_subparser_main():
    """
    Create a main function that uses subparsers instead of the monolithic approach.
    This is a replacement for the main() function in crypt_cli.py
    """
    # Set up main argument parser with subcommands
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt files with password protection\n\nEnvironment Variables:\n  CRYPT_PASSWORD    Password for encryption/decryption (alternative to -p)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Global options
    parser.add_argument("--progress", action="store_true", help="Show progress bar")
    parser.add_argument("--verbose", action="store_true", help="Show hash/kdf details")
    parser.add_argument("--debug", action="store_true", help="Show detailed debug information")
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress all output except decrypted content and exit code",
    )

    # Create subparsers for each command
    subparsers = parser.add_subparsers(
        dest="action",
        help="Available commands",
        metavar="command",
    )

    # Set up subparsers for each command
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        help="Encrypt files with password protection",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_encrypt_parser(encrypt_parser)

    decrypt_parser = subparsers.add_parser(
        "decrypt",
        help="Decrypt previously encrypted files",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_decrypt_parser(decrypt_parser)

    shred_parser = subparsers.add_parser(
        "shred",
        help="Securely delete files",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_shred_parser(shred_parser)

    generate_password_parser = subparsers.add_parser(
        "generate-password",
        help="Generate cryptographically secure passwords",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_generate_password_parser(generate_password_parser)

    security_info_parser = subparsers.add_parser(
        "security-info",
        help="Display security information and algorithms",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_simple_parser(security_info_parser)

    check_argon2_parser = subparsers.add_parser(
        "check-argon2",
        help="Verify Argon2 implementation",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_simple_parser(check_argon2_parser)

    check_pqc_parser = subparsers.add_parser(
        "check-pqc",
        help="Check post-quantum cryptography support",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_simple_parser(check_pqc_parser)

    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_simple_parser(version_parser)

    show_version_file_parser = subparsers.add_parser(
        "show-version-file",
        help="Show detailed version file information",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    setup_simple_parser(show_version_file_parser)

    # Parse arguments
    args = parser.parse_args()

    # Handle the case where no command is provided
    if args.action is None:
        parser.print_help()
        return 1

    return parser, args
