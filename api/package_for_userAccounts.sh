#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf userAccounts_lambda.zip
rm -rf userAccounts-lib

# pip install -t lib -r requirements.txt
# (cd lib; zip ../userAccounts_lambda.zip -r .)
# zip userAccounts_lambda.zip -u userAccounts.py

# # Clean up
# rm -rf lib

#  Package
pip install -t userAccounts-lib -r userAccounts/requirements.txt
(cd userAccounts-lib; zip ../userAccounts_lambda.zip -r .)
zip userAccounts_lambda.zip -u userAccounts/__init__.py
zip userAccounts_lambda.zip -u userAccounts/router.py
zip userAccounts_lambda.zip -u userAccounts/models.py
zip userAccounts_lambda.zip -u userAccounts/dynamo.py
zip userAccounts_lambda.zip -u userAccounts/utils.py

# Clean up
rm -rf userAccounts-lib