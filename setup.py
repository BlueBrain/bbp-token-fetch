from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="blue_brain_token_fetch",
    author="Blue Brain Project, EPFL",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Package to perform fetching and automatic refreshing of the Nexus "
    "access token using Keycloak. Using the CLI you can choose to either have its "
    "value periodically written in the file whose path is given in input or either "
    "have it periodically printed on the console output.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BlueBrain/bbp-token-fetch",
    license="Apache-2.0",
    python_requires=">=3.6.0",
    install_requires=[
        "click>=7.0",
        "python-keycloak>=0.24.0",
        "PyYAML>=5.3.1",
    ],
    extras_require={
        "dev": [
            "pytest>=4.3.0",
            "pytest-cov==4.1.0",
            "pycodestyle==2.11.1",
            "pylint==3.0.2"
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "blue-brain-token-fetch=blue_brain_token_fetch.nexus_token_fetch:start"
        ]
    },
)
