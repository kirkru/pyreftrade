#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf *.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../symbol_lambda.zip -r .)
zip symbol_lambda.zip -u symbol.py

(cd lib; zip ../reviewOrder_lambda.zip -r .)
zip reviewOrder_lambda.zip -u reviewOrder.py

(cd lib; zip ../ordering_lambda.zip -r .)
zip ordering_lambda.zip -u ordering.py

# Clean up
rm -rf lib