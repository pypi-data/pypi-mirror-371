#!/usr/bin/env python3
import argparse
import os
import gnupg
from mpgkit.keymanager import import_key, export_key, list_keys

# Initialize GPG
gpg = gnupg.GPG(gnupghome=os.path.expanduser("~/.gnupg"))
gpg.encoding = "utf-8"


# -----------------------------
# Encryption / Decryption
# -----------------------------
def encrypt(args):
    key = args.key

    # If key is a file, import it
    if os.path.isfile(key):
        fingerprints = import_key(key)
        recipient = fingerprints[0]  # Use first fingerprint # type:ignore
    else:
        recipient = key  # Assume key is in keyring

    if os.path.isfile(args.input):
        # Encrypt a file
        output_file = args.output or f"{args.input}.pgp"
        with open(args.input, "rb") as f:
            status = gpg.encrypt_file(f, recipients=[recipient], output=output_file)
        if status.ok:
            print(f"[+] File encrypted: {output_file}")
        else:
            print(f"[!] Encryption failed: {status.status}")
    else:
        # Encrypt a string
        status = gpg.encrypt(args.input, recipients=[recipient])
        if status.ok:
            if args.output:
                with open(args.output, "w") as f:
                    f.write(str(status))
                print(f"[+] String encrypted -> file: {args.output}")
            else:
                print(f"[+] Encrypted string:\n{status}")
        else:
            print(f"[!] Encryption failed: {status.status}")


def decrypt(args):
    key = args.key

    # If key is a file, import it
    if os.path.isfile(key):
        fingerprints = import_key(key)
        private_key = fingerprints[0]  # type:ignore
    else:
        private_key = key  # Assume key is in keyring

    if os.path.isfile(args.input):
        # Decrypt a file
        output_file = args.output or f"{args.input}.dec"
        with open(args.input, "rb") as f:
            status = gpg.decrypt_file(f, passphrase=None, output=output_file)
        if status.ok:
            print(f"[+] File decrypted: {output_file}")
        else:
            print(f"[!] Decryption failed: {status.status}")
    else:
        # Decrypt a string
        status = gpg.decrypt(args.input, passphrase=None)
        if status.ok:
            if args.output:
                with open(args.output, "w") as f:
                    f.write(str(status))
                print(f"[+] String decrypted -> file: {args.output}")
            else:
                print(f"[+] Decrypted string:\n{status}")
        else:
            print(f"[!] Decryption failed: {status.status}")


# -----------------------------
# Main CLI
# -----------------------------
def main():
    parser = argparse.ArgumentParser(description="mPGkit - Matel's PGP toolkit")
    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    # Encrypt subcommand
    enc_parser = subparsers.add_parser("enc", help="Encrypt a file or string")
    enc_parser.add_argument("input", help="File path or string to encrypt")
    enc_parser.add_argument("-o", "--output", help="Output file (if input is a file)")
    enc_parser.add_argument(
        "-k",
        "--key",
        required=True,
        help="Public PGP key (key ID or .asc file) to encrypt with",
    )
    enc_parser.set_defaults(func=encrypt)

    # Decrypt subcommand
    dec_parser = subparsers.add_parser("dec", help="Decrypt a file or string")
    dec_parser.add_argument("input", help="File path or string to decrypt")
    dec_parser.add_argument("-o", "--output", help="Output file (if input is a file)")
    dec_parser.add_argument(
        "-k",
        "--key",
        required=True,
        help="Private PGP key (key ID or .asc file) to decrypt with",
    )
    dec_parser.set_defaults(func=decrypt)

    # Key management commands
    imp_parser = subparsers.add_parser("import", help="Import a key into keyring")
    imp_parser.add_argument("file", help="Path to .asc key file")
    imp_parser.set_defaults(func=lambda args: import_key(args.file))

    exp_parser = subparsers.add_parser("export", help="Export a key from keyring")
    exp_parser.add_argument("key_id", help="Key ID or fingerprint to export")
    exp_parser.add_argument(
        "-s", "--secret", action="store_true", help="Export private key"
    )
    exp_parser.add_argument("-o", "--output", help="Output file (default: stdout)")
    exp_parser.set_defaults(
        func=lambda args: export_key(args.key_id, not args.secret, args.output)
    )
    exp_parser.add_argument(
        "-p", "--passphrase", help="Passphrase for private key export"
    )
    exp_parser.set_defaults(
        func=lambda args: export_key(
            args.key_id, not args.secret, args.output, args.passphrase
        )
    )

    list_parser = subparsers.add_parser("list", help="List keys in keyring")
    list_parser.add_argument(
        "-s", "--secret", action="store_true", help="List private keys"
    )
    list_parser.set_defaults(func=lambda args: list_keys(not args.secret))

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
