from setuptools import setup, find_packages

setup(
    name="passguard-assistant",
    version="0.3.2",
    description="PassGuard Assistant - Password health, hashing, and security toolkit",
    author="Sathish J",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "argon2-cffi>=21.3.0",
        "bcrypt>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "passguard=passguard_assistant.cli:main",
        ],
    },
)
