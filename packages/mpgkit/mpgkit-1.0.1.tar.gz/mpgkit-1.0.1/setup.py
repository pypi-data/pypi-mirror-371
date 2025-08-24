from setuptools import setup, find_packages
from pathlib import Path

# Read the README.md file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mpgkit",
    version="1.0.1",
    author="Matel",
    description="mPGkit - Matel's PGP toolkit",
    long_description=long_description,  # <-- use README.md
    long_description_content_type="text/markdown",  # <-- must specify markdown
    packages=find_packages(),
    install_requires=["python-gnupg"],
    entry_points={
        "console_scripts": [
            "mpgkit=mpgkit.cli:main",
        ],
    },
    python_requires=">=3.8",
)
