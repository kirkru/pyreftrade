# To-do List API: A FastAPI CRUD App


curl -X 'GET' \
--url 'http://127.0.0.1:8000/api/private' \
--header  'Authorization: Bearer <YOUR_BEARER_TOKEN>'


curl -X 'GET' \
--url 'http://127.0.0.1:8000/api/private' \
--header  'Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpFWnlZUWRzRTgtY203THBKZ3RERiJ9.eyJpc3MiOiJodHRwczovL2Rldi01LTh6ZzR3MC51cy5hdXRoMC5jb20vIiwic3ViIjoiQlVjSXlrSVFEamY5UGhmWkRWZFFiZkZCRENxam9hcXJAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vcmVmdHJhZGUvYXBpIiwiaWF0IjoxNjYzODkyMjM4LCJleHAiOjE2NjM5Nzg2MzgsImF6cCI6IkJVY0l5a0lRRGpmOVBoZlpEVmRRYmZGQkRDcWpvYXFyIiwiZ3R5IjoiY2xpZW50LWNyZWRlbnRpYWxzIn0.vzVgNIkjhi-ky_afcnFNBCKNDaz9d7NAbd8nx6tk_tZblNMAMU5VlDRsM2RWM2wbYAz-U6DQ9eI58_cNkBLSiKDYDPyu92nI3NXQSg6RVsEP4F29YRMr_t11cicd26uDv4YD7YbnrLwB5AzMLEhsZGgbUHN7p7KE4PV2KZnjDVhP9-2gJnGp-UbcrWxRzCstWqd_4EUFTrKSLHLJAMdsGP8F6_tQ_Cs5yRxc_z4P7T-FDmWpA1aAgQGi3OCU45YAfra9yIdE3e4FXVqmIyIXfAMDaopLHmmLRY63KcEYQgzjPMBkhb-JAKwHvanV6LXwmiI4hJ-hHdgLaqasRRSx5Q'

https://manage.auth0.com/dashboard/us/dev-5-8zg4w0/apis/632cef6f52efe7a28a11c4ec/test

https://auth0.com/blog/build-and-secure-fastapi-server-with-auth0/

This project is a full-stack CRUD app (a trade-list) with a Python FastAPI backend and a
NextJS frontend. It is hosted on serverless AWS infrastructure (using Lambda and DynamoDB).

![Task API app](task_api.png)

## API Folder

The `/api` folder contains the Python FastAPI code. Run this shell script to build the code into
a zip (required for CDK to upload to Lambda):

```bash
# Only work on UNIX (Mac/Linux) systems!
./package_for_lambda.sh
```

This should generate a `lambda_function.zip`.

## Infrastructure Folder

The `/trade-infra` folder contains the CDK code to deploy all the infrastructure 
(Lambda function and DynamoDB table) to your AWS account.

You must have [AWS CLI](https://aws.amazon.com/cli/) configured, and 
[AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html) installed on your machine.

First, install the node modules.

```bash
npm install
```

Then run bootstrap if you never used CDK with your account before.

```bash
cdk bootstrap
```

Now you can use this to deploy.

```bash
cdk deploy
```

## Frontend Folder

The `/trade-site` contains the NextJS frontend that interfaces with the CRUD API. If you want to
test it with your endpoint, then don't forget to change `tradeApiEndpoint` and `userId` to your own
API (in `pages/index.tsx`).

Install the node modules.

```bash
npm install
```

Run the development server locally.

```bash
npm run dev
```

## Test Folder

This contains the Pytest integration tests you can use to test your endpoint directly. Don't 
forget to change your `ENDPOINT` to the one you want to use (in `api_integration_test.py`).

You can run the test like this (but you have to have `pytest` installed):

```bash
pytest
```


