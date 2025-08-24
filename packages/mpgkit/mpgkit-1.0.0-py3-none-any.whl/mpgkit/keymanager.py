import os
import gnupg

# Initialize GPG
gpg = gnupg.GPG(gnupghome=os.path.expanduser("~/.gnupg"))
gpg.encoding = "utf-8"


def import_key(file_path):
    """Import a key from an external file into the user keyring."""
    if not os.path.isfile(file_path):
        print(f"[!] Key file not found: {file_path}")
        return
    with open(file_path, "rb") as f:
        result = gpg.import_keys(f.read())
        gpg.trust_keys(result.fingerprints, "TRUST_ULTIMATE")
    print(f"[+] Imported key(s) with fingerprints: {', '.join(result.fingerprints)}")
    return result.fingerprints


def export_key(key_id, public=True, output_file=None, passphrase=None):
    """Export a public or private key from the keyring."""
    if public:
        key_data = gpg.export_keys(key_id, armor=True)
    else:
        key_data = gpg.export_keys(
            key_id, secret=True, armor=True, passphrase=passphrase
        )

    if not key_data:
        print(f"[!] Key not found in keyring: {key_id}")
        return

    if output_file:
        with open(output_file, "w") as f:
            f.write(key_data)
        print(f"[+] Key exported to {output_file}")
    else:
        print(f"[+] Key data:\n{key_data}")


def list_keys(public=True):
    """List keys in the keyring."""
    keys = gpg.list_keys() if public else gpg.list_keys(secret=True)
    if not keys:
        print("[!] No keys found.")
        return
    for key in keys:
        key_type = "Public" if public else "Private"
        print(f"{key_type} key: {key['uids'][0]} | Fingerprint: {key['fingerprint']}")
