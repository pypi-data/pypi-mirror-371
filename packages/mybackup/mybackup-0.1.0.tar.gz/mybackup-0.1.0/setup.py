from setuptools import setup, find_packages

setup(
    name="mybackup",
    version="0.1.0",
    description="Terminal-based website backup and info tool",
    author="father gg",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-whois"
    ],
    entry_points={
        "console_scripts": [
            "mybackup=mybackup.cli:main",
        ],
    },
)
