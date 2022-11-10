#!/bin/bash

# Exit if any command fails
set -eux pipefail

# Package lambda
cd ../app
./package_fastapi_lambda.sh

# Deploy infrastructure and lambda changes
cd ../infra
cdk deploy
