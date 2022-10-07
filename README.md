# References

https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/WorkingWithItemCollections.html

https://stackoverflow.com/questions/26033239/list-of-objects-to-json-with-python

https://www.geeksforgeeks.org/convert-class-object-to-json-in-python/

https://ysk24ok.github.io/2021/09/02/difference_between_def_and_async_def_in_fastapi.html

Batch writes
https://stackoverflow.com/questions/60267884/how-to-insert-list-of-objects-in-1-write-to-dynamodb-using-python

https://medium.com/skyline-ai/dynamodb-insert-performance-basics-in-python-boto3-5bc01919c79f

# Reference Trading Demo API

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


