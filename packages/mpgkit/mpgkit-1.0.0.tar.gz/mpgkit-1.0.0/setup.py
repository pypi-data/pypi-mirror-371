from setuptools import setup, find_packages

setup(
    name="mpgkit",
    version="1.0.0",
    author="Matel",
    description="mPGkit - Matel's PGP toolkit",
    packages=find_packages(),
    install_requires=["python-gnupg"],
    entry_points={
        "console_scripts": [
            "mpgkit=mpgkit.cli:main",  # lowercase folder name
        ],
    },
    python_requires='>=3.8',
)
