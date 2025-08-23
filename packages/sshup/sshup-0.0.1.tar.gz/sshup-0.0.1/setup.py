from setuptools import setup, find_packages
import sshup

setup(
    name="sshup",
    version=sshup.__version__,
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "sshup=sshup.main:main",
        ],
    },
    include_package_data=True,
    description="A simple SSH Manager",
    url="https://github.com/wmramadan/sshup",
    author=sshup.__author__,
    author_email=sshup.__email__,
    maintainer=sshup.__maintainer__,
    maintainer_email=sshup.__email__,
    python_requires=">=3.7",
    license=(
        "License :: OSI Approved :: MIT License"
    ),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Other Audience",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities"
    ]
)
