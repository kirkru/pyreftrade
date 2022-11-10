#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf *.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../instrument_lambda.zip -r .)
zip instrument_lambda.zip -u instrument.py

(cd lib; zip ../userAccounts_lambda.zip -r .)
zip userAccounts_lambda.zip -u userAccounts.py

(cd lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder.py

(cd lib; zip ../trading_lambda.zip -r .)
zip trading_lambda.zip -u trading.py

# Clean up
rm -rf lib