#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf instruments_lambda.zip

pip install -t lib -r instruments/requirements.txt
(cd lib; zip ../instruments_lambda.zip -r .)
zip instruments_lambda.zip -u instruments/__init__.py
zip instruments_lambda.zip -u instruments/router.py
zip instruments_lambda.zip -u instruments/models.py
zip instruments_lambda.zip -u instruments/dynamo.py
zip instruments_lambda.zip -u instruments/utils.py

# Clean up
rm -rf lib