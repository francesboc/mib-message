#!/usr/bin/env python

import ast
import re

from setuptools import setup, find_packages

_version_re = re.compile(r"__version__\s+=\s+(.*)")

PROJECT = "MessaInABottle"

with open(PROJECT + "/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

setup(
    name=PROJECT,
    version=version,
    author="SQUAD <ID>",
    license="BSD 3-clause",
    packages=find_packages(),
    include_package_data=True,
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    zip_safe=False
)
