#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf ordering_lambda.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../ordering_lambda.zip -r .)
zip ordering_lambda.zip -u ordering.py

# Clean up
rm -rf lib