#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf trading_lambda.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../trading_lambda.zip -r .)
zip trading_lambda.zip -u trading.py

# Clean up
rm -rf lib