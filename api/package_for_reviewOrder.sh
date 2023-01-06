#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf reviewOrder_lambda.zip
rm -rf reviewOrder-lib

#  Package
pip install -t reviewOrder-lib -r reviewOrder/requirements.txt
(cd reviewOrder-lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder/__init__.py
zip reviewOrder_lambda.zip -u reviewOrder/router.py
zip reviewOrder_lambda.zip -u reviewOrder/models.py
zip reviewOrder_lambda.zip -u reviewOrder/dynamo.py
zip reviewOrder_lambda.zip -u reviewOrder/utils.py

# Clean up
rm -rf reviewOrder-lib
