#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip files and lib folders
rm -rf *.zip
rm -rf instruments-lib
rm -rf reviewOrder-lib
rm -rf trading-lib
rm -rf userAccounts-lib

#  Package

# pip install -t lib -r requirements.txt
# (cd lib; zip ../instrument_lambda.zip -r .)
# zip instrument_lambda.zip -u instrument.py

pip install -t instruments-lib -r instruments/requirements.txt
(cd instruments-lib; zip ../instruments_lambda.zip -r .)
zip instruments_lambda.zip -u instruments/__init__.py
zip instruments_lambda.zip -u instruments/router.py
zip instruments_lambda.zip -u instruments/models.py
zip instruments_lambda.zip -u instruments/dynamo.py
zip instruments_lambda.zip -u instruments/utils.py

pip install -t reviewOrder-lib -r reviewOrder/requirements.txt
(cd reviewOrder-lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder/__init__.py
zip reviewOrder_lambda.zip -u reviewOrder/router.py
zip reviewOrder_lambda.zip -u reviewOrder/models.py
zip reviewOrder_lambda.zip -u reviewOrder/dynamo.py
zip reviewOrder_lambda.zip -u reviewOrder/utils.py

pip install -t userAccounts-lib -r userAccounts/requirements.txt
(cd userAccounts-lib; zip ../userAccounts_lambda.zip -r .)
zip userAccounts_lambda.zip -u userAccounts/__init__.py
zip userAccounts_lambda.zip -u userAccounts/router.py
zip userAccounts_lambda.zip -u userAccounts/models.py
zip userAccounts_lambda.zip -u userAccounts/dynamo.py
zip userAccounts_lambda.zip -u userAccounts/utils.py

pip install -t trading-lib -r trading/requirements.txt
(cd trading-lib; zip ../trading_lambda.zip -r .)
zip trading_lambda.zip -u trading/__init__.py
zip trading_lambda.zip -u trading/router.py
zip trading_lambda.zip -u trading/models.py
zip trading_lambda.zip -u trading/dynamo.py
zip trading_lambda.zip -u trading/utils.py

# Clean up
# rm -rf instruments-lib
# rm -rf reviewOrder-lib
# rm -rf trading-lib
# rm -rf userAccounts-lib