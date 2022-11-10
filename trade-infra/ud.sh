#!/bin/bash

# ReviewOrder Lambda deploy

# Exit if any command fails
set -eux pipefail

# Package lambda
cd ../api
./package_for_userAccounts.sh

# Deploy infrastructure and lambda changes
cd ../trade-infra
cdk deploy
