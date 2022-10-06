#!/bin/bash

# Exit if any command fails
set -eux pipefail

cd ../api
./package_for_lambda.sh

cd ../trade-infra
cdk deploy --require-approval never
