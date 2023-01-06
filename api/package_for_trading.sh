#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf trading_lambda.zip
rm -rf trading-lib

# pip install -t lib -r requirements.txt
# (cd lib; zip ../trading_lambda.zip -r .)
# zip trading_lambda.zip -u trading.py

# # Clean up
# rm -rf lib

#  Package
pip install -t trading-lib -r trading/requirements.txt
(cd trading-lib; zip ../trading_lambda.zip -r .)
zip trading_lambda.zip -u trading/__init__.py
zip trading_lambda.zip -u trading/router.py
zip trading_lambda.zip -u trading/models.py
zip trading_lambda.zip -u trading/dynamo.py
zip trading_lambda.zip -u trading/utils.py

# Clean up
rm -rf trading-lib