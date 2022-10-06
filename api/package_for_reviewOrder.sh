#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf reviewOrder_lambda.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder.py

# Clean up
rm -rf lib