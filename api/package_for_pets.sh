#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf pets_lambda.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../pets_lambda.zip -r .)
zip pets_lambda.zip -u pets/__init__.py
zip pets_lambda.zip -u pets/router.py
zip pets_lambda.zip -u pets/models.py
zip pets_lambda.zip -u pets/dynamo.py
zip pets_lambda.zip -u pets/utils.py

# Clean up
rm -rf lib