#!/bin/bash

echo "Running test suite with coverage report at the end"
echo -e "( would require coverage python package to be installed )\n"

OMIT="monolith/compat.py,monolith/tests/__init__.py"
coverage run setup.py test
coverage report -m --include "monolith/*" --omit $OMIT
