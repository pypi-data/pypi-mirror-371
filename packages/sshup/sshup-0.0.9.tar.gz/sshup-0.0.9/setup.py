from pathlib    import Path
from setuptools import setup, find_packages
import sshup

##############################################################################
# Work out the location of the README file.
def readme():
    """Return the full path to the README file.
    :returns: The path to the README file.
    :rtype: ~pathlib.Path
    """
    return Path( __file__ ).parent.resolve() / "README.md"

##############################################################################
# Load the long description for the package.
def long_desc():
    """Load the long description of the package from the README.
    :returns: The long description.
    :rtype: str
    """
    with readme().open( "r", encoding="utf-8" ) as rtfm:
        return rtfm.read()

##############################################################################
# python3 -m build 
# Setup.
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
    description=str( sshup.__doc__ ),
    long_description=long_desc(),
    long_description_content_type="text/markdown",
    url="https://github.com/wmramadan/sshup-tui",
    author=sshup.__author__,
    author_email=sshup.__email__,
    maintainer=sshup.__maintainer__,
    maintainer_email=sshup.__email__,
    python_requires=">=3.9",
    license=(
        "License :: OSI Approved :: MIT License"
    ),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Other Audience",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: BSD :: FreeBSD",
        "Operating System :: POSIX :: BSD :: OpenBSD",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities"
    ]
)
