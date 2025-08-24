# mPGkit 🔑

**mPGkit** (Matel’s PGP toolkit) is a lightweight, Python-powered toolkit for performing **PGP encryption, decryption, signing, and verification** on files and strings.  
It’s built with [python-gnupg](https://pypi.org/project/python-gnupg/) and designed to feel like a natural UNIX-style CLI tool.

---

## ✨ Features
- 🔒 Encrypt & decrypt files and strings with PGP  
- 🖊️ Sign and verify messages or documents  
- 🔑 Manage keys (import, export, list)  
- 🛠️ Easy CLI commands (`mpgkit enc …`, `mpgkit dec …`)

---

## 📦 Installation

```bash
# Using pipx (recommended for CLI isolation)
pipx install git+https://gitlab.com/matelowy/mpgkit.git # Development version
pipx install mpgkit # Stable version

# Or using pip
pip install mpgkit # Stable version
pip install git+https://gitlab.com/matelowy/mpgkit.git # Development version
````

---

## 💡 Usage Examples

### List all keys in your keyring

```bash
mpgkit list
```

### Import a key

```bash
mpgkit import mykey.asc
```

### Export a key

```bash
# Export public key
mpgkit export -p 8D91D7XXXXXXXX77509C0895E449YYYYYYYY9D2A -o mypublic.asc

# Export private key (requires passphrase)
mpgkit export -s 8D91D7XXXXXXXX77509C0895E449YYYYYYYY9D2A -o myprivate.asc -p "mySecretPassphrase"
```

### Encrypt a file or string

```bash
# Encrypt a string
mpgkit enc "Hello world" -k recipient_pubkey.asc

# Encrypt a file
mpgkit enc /path/to/file.txt -k recipient_pubkey.asc -o encrypted_file.gpg
```

### Decrypt a file or string

```bash
# Decrypt a string
mpgkit dec "encrypted string" -k my_privatekey.asc

# Decrypt a file
mpgkit dec /path/to/encrypted_file.gpg -k my_privatekey.asc -o decrypted_file.txt
```

---

## 📜 License

**mPGkit** is licensed under the **GPL-3.0 License**.
You are free to use, modify, and redistribute it, **but derivative projects must also be open-source and credit Matel**.

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Make changes
3. Submit a merge request

---

## 🌐 Contact

Matel – [GitLab](https://gitlab.com/matelowy)
