#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf *.zip

pip install -t lib -r pets/requirements.txt
(cd lib; zip ../pets_lambda.zip -r .)
zip pets_lambda.zip -u pets/__init__.py
zip pets_lambda.zip -u pets/router.py
zip pets_lambda.zip -u pets/models.py
zip pets_lambda.zip -u pets/dynamo.py
zip pets_lambda.zip -u pets/utils.py

pip install -t instruments-lib -r instruments/requirements.txt
(cd instruments-lib; zip ../instruments_lambda.zip -r .)
zip instruments_lambda.zip -u instruments/__init__.py
zip instruments_lambda.zip -u instruments/router.py
zip instruments_lambda.zip -u instruments/models.py
zip instruments_lambda.zip -u instruments/dynamo.py
zip instruments_lambda.zip -u instruments/utils.py

# pip install -t lib -r requirements.txt
# (cd lib; zip ../instrument_lambda.zip -r .)
# zip instrument_lambda.zip -u instrument.py

(cd lib; zip ../userAccounts_lambda.zip -r .)
zip userAccounts_lambda.zip -u userAccounts.py

(cd lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder.py

(cd lib; zip ../trading_lambda.zip -r .)
zip trading_lambda.zip -u trading.py

# Clean up
rm -rf lib

# Clean up
rm -rf instruments-lib
