#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf userAccounts_lambda.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../userAccounts_lambda.zip -r .)
zip userAccounts_lambda.zip -u userAccounts.py

# Clean up
rm -rf lib