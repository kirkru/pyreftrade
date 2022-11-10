#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Clean previous zip
rm -rf *.zip

pip install -t lib -r requirements.txt
(cd lib; zip ../main_function.zip -r .)
zip -g ./main_function.zip -r ../app

# Clean up
rm -rf lib