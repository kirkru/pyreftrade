import json
from urllib import response
import uuid
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from decimal import Decimal
import boto3
import os
from fastapi import FastAPI, HTTPException
# import boto3
from botocore.exceptions import ClientError

# from enum import Enum
 
# class AccountType(Enum):
#     Brokerage = 1
#     TraditionalIRA = 2
#     RothIRA = 3
#     Trust = 4

# Sample event 
'''

# User Profile
{
  "userName": "kir",
  "address": "323 adsdf",
  "zip": 75070,
  "state": "TX",
  "country": "USA",
  "dob": "2001-01-01" 
}

{
  "userName": "kir",
  "accountId": "acc123",
  "totalPrice": 0.0,
  "orderItems": [
    {
      "quantity": 2,
      "price": 140,
      "instrumentId": "AAPL",
      "instrumentName": "Apple Inc."
    },
    {
      "quantity": 1,
      "price": 90,
      "instrumentId": "XOM",
      "instrumentName": "Exxon Mobil Inc."
    }
  ]
}
{
  "userName": "kir",
  "address": "343 sdfad",
  "zip": "77575",
  "state": "TX",
  "country": "USA",
  "dob": "2000-10-28" 
}
'''

'''
{"userName": "kir","address": "343 sdfad","zip": "77575","state": "TX","country": "USA","dob": "2022-10-28"}

'''
class DictObj:
    def __init__(self, in_dict:dict):
        assert isinstance(in_dict, dict)
        for key, val in in_dict.items():
            if isinstance(val, (list, tuple)):
               setattr(self, key, [DictObj(x) if isinstance(x, dict) else x for x in val])
            else:
               setattr(self, key, DictObj(val) if isinstance(val, dict) else val)            


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        # 👇️ if passed in object is instance of Decimal
        # convert it to a string
        if isinstance(obj, Decimal):
            return str(obj)
        # 👇️ otherwise use the default behavior
        return json.JSONEncoder.default(self, obj)

  
class Dict2Class(object):
      
    def __init__(self, my_dict):
          
        for key in my_dict:
            setattr(self, key, my_dict[key])

class UserProfileRequest:
  userName: str
  address: str
  zip: str
  state: str
  country: str
  dob: datetime 

class UserAccountRequest:
  userName: str
  accountID: str
  nickname: str
  cash_balance: float

class AccountHoldingRequest:
  accountID: str
  instrument: str
  quantity: float
  unit_price: float

#region CONSTANTS
USER_PROFILE_DATA_FIELD = "profile"
ACCOUNTS_PREFIX = "acc#"
USER_PREFIX = "user#"
HOLDING_PREFIX = "holding#"
ACC_HOLDING_PREFIX = "accHolding#"
#endregion

def handler(event, context):
  print("Event:", event)
  print("Context:", context)

  try :

    path = event['path']
    print(path)
    process_request = get_process_request_function(event)
    return process_request(event)

  except Exception as e:
    print("Error Occured while processing request: ", e)

# GET /userProfile/{userName}
# GET /userAccounts/{userName}
# GET /accountHoldings/{accountID}
# GET /holdingInAccounts/{holdingID}

# POST /userProfile
# POST /userAccounts
# POST /accountHoldings

# Route to the appropriate method 

# @dataclass

# def get_event_entities(event):

#region Helper methods
def json_response(responseItem, data, code):
  payload = json.dumps({responseItem : data}, indent=4, cls=DecimalEncoder)
  response = {
    'isBase64Encoded': False,
    'statusCode': code,
    'headers': {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*'
    },
    'body': payload
  }
  return response
  # return json.dumps(response)

def error_response(event):
    print("Error occured with: ", event['httpMethod'])

def get_process_request_function(event):

  httpMethod = event['httpMethod']
  path_params = event['pathParameters']
  resource = event['resource']

  print("process_request:", httpMethod, resource)

  resource_switcher = {
    "/user": "user_profile",
    "/userAccounts": "user_accounts",
    "/accountHoldings": "account_holdings",
    "/holdingInAccounts": "holding_in_accounts"
  }
  resource_function = resource_switcher.get(resource)

  switcher = {
    "GET": eval("get_" + resource_function),
    "POST": eval("create_" + resource_function),
    "DELETE": eval("delete_" + resource_function),
    "PUT": eval("update_" + resource_function)
  }

  return switcher.get(httpMethod, error_response)

def check_query_params(event):
  query_params = event['queryStringParameters']

  if (query_params):
    print(query_params)
    return query_params
  else:
    print("Invalid request. No query params. Request either user, account or holdings information")
    raise Exception("Invalid request. No query params. Request either user, account or holdings information")

def get_request_from_body(event):
  body = event['body']
  bodyD = json.loads(body)
  print (body)
  requestObject = Dict2Class(bodyD)
  return requestObject

#endregion

#region /user API
def update_user_profile(event):
  print("update_user_profile")
  try:
    userProfileRequest = get_request_from_body(event)
    profileUpdationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    table = _get_table()

    response = table.update_item(
        Key={
            'PK': USER_PREFIX + userProfileRequest.userName,
            'SK': USER_PROFILE_DATA_FIELD
        },
        UpdateExpression="set #address=:a, #zip=:z, #state=:s, #country=:c, #dob=:d, #profile_update_time=:u",
        ExpressionAttributeNames={
            "#address": "address",
            "#zip": "zip",
            "#state": "state",
            "#country": "country",
            "#dob": "dob",
            "#profile_update_time": "profile_update_time"
        },
        ExpressionAttributeValues={
            ":a": userProfileRequest.address,
            ":z": userProfileRequest.zip,
            ":s": userProfileRequest.state,
            ":c": userProfileRequest.country,
            ":d": userProfileRequest.dob,
            ":u": profileUpdationTime
        },
        ReturnValues="UPDATED_NEW"
    )
    r2 = json_response("Updated Item", userProfileRequest.__dict__, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("UpdateItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def delete_user_profile(event):
  print("delete_user_profile")
  try:
    qp = check_query_params(event)

    userName = qp.get("username")
  
    table = _get_table()

    response = table.delete_item(
        Key={
            'PK': USER_PREFIX + userName,
            'SK': USER_PROFILE_DATA_FIELD
        }
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)
    r2 = json_response("Deleted Item", response, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("DeleteItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def get_user_profile(event):
  print("get_user_profile")
  try:

    qp = check_query_params(event)

    userName = qp.get("username")

    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.query(
        TableName=os.environ.get("USERACCOUNTS_TABLE_NAME"),
        KeyConditionExpression='PK = :PK AND SK = :SK',
        ExpressionAttributeValues={
            ':PK': {'S': USER_PREFIX + userName.lower()},
            ':SK': {'S': USER_PROFILE_DATA_FIELD}
        }
    )
    print(response['Items'])
    items = response['Items']
    r2 = json_response("User Info", items, 200)

    if not items:
      print("No items queried")
      error_response = json_response("Error", "Empty result", 404)
      return error_response
      # raise HTTPException(status_code=404, detail=f"User: {userName} not found")
    
    # r = {
    #     "statusCode": 200,
    #     "headers": {
    #       "Content-Type": "application/json"
    #     },
    #     "body": json.dumps(items)
    # }
    # print(r)
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise
    # if e.response['Error']['Code'] == "ConditionalCheckFailedException":
    #   print(e.response['Error']['Message'])
    # else:
    #   raise
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def create_user_profile(event):
  print("create_user_profile")

  try:
    userProfileRequest = get_request_from_body(event)
    # body = event['body']
    # bodyD = json.loads(body)
    # print (body)
    # userProfileRequest = Dict2Class(bodyD)
    # return create_profile(userProfileRequest)
    # Create the user profile
    userCreationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(userProfileRequest)
    print(type(userProfileRequest))
    userName = USER_PREFIX + userProfileRequest.userName.lower()
    # dob = userProfileRequest.dob.strftime('%Y-%m-%d')
    item = {
        "PK": userName,
        "SK": USER_PROFILE_DATA_FIELD,
        "address": userProfileRequest.address,
        "zip": userProfileRequest.zip,
        "state": userProfileRequest.state,
        "country": userProfileRequest.country,
        "dob": userProfileRequest.dob,
    }

    # Put item into the table.
    table = _get_table()
    response = table.put_item(Item=item)

    r2 = json_response("User Created", item, 200)
    print(r2)
    # jr = json.dumps(response)
    # print(jr)
    # return jr
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise
    # if e.response['Error']['Code'] == "ConditionalCheckFailedException":
    #   print(e.response['Error']['Message'])
    # else:
    #   raise
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  r2 = json_response("User Created", item, 200)
  return r2
  # except Exception as e:
  #   print("Exception occured:", e)
  #   return {"Exception occured": str(e) }

#endregion

#region /userAccounts API
def get_user_accounts(event):
  print("get_user_accounts")
  try:

    qp = check_query_params(event)

    userName = qp.get("username")

    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.query(
        TableName=os.environ.get("USERACCOUNTS_TABLE_NAME"),
        KeyConditionExpression='PK = :PK AND begins_with (SK, :SK)',
        ExpressionAttributeValues={
            ':PK': {'S': USER_PREFIX + userName.lower()},
            ':SK': {'S': ACCOUNTS_PREFIX}
        }
    )
    print(response['Items'])
    items = response['Items']
    r2 = json_response("User Info", items, 200)

    if not items:
      print("No items queried")
      error_response = json_response("Error", "Empty result", 404)
      return error_response
      # raise HTTPException(status_code=404, detail=f"User: {userName} not found")
    
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def update_user_accounts(event):
  print("update_user_accounts")
  try:
    userAccountRequest = get_request_from_body(event)
    accountUpdationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    table = _get_table()

    response = table.update_item(
        Key={
            'PK': USER_PREFIX + userAccountRequest.userName,
            'SK': ACCOUNTS_PREFIX + userAccountRequest.accountID
        },
        UpdateExpression="set #nickname=:n, #cash_balance=:c, #acc_update_time=:u",
        ExpressionAttributeNames={
            "#nickname": "nickname",
            "#cash_balance": "cash_balance",
            "#acc_update_time": "acc_update_time"
        },
        ExpressionAttributeValues={
            ":n": userAccountRequest.nickname,
            ":c": Decimal(str(userAccountRequest.cash_balance)),
            ":u": accountUpdationTime
        },
        ReturnValues="UPDATED_NEW"
    )
    r2 = json_response("Updated Item", userAccountRequest.__dict__, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("UpdateItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def create_user_accounts(event):
  print("create_user_accounts")

  try:
    userAccountRequest = get_request_from_body(event)
    # Create the user account
    accountCreationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(userAccountRequest)
    print(type(userAccountRequest))
    userName = USER_PREFIX + userAccountRequest.userName.lower()
    accountID = ACCOUNTS_PREFIX + str(uuid.uuid4())
    # dob = userProfileRequest.dob.strftime('%Y-%m-%d')
    item = {
        "PK": userName,
        "SK": accountID,
        "cash_balance": Decimal(str(userAccountRequest.cash_balance)),
        "nickname": userAccountRequest.nickname,
        "accountCreationTime": accountCreationTime
    }

    # Put item into the table.
    table = _get_table()
    response = table.put_item(Item=item)

    r2 = json_response("Account Created", item, 200)
    print(r2)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e

  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def delete_user_accounts(event):
  print("delete_user_accounts")
  try:
    qp = check_query_params(event)

    accountID = qp.get("accountID")
    userName = qp.get("username")

    table = _get_table()

    response = table.delete_item(
        Key={
            'PK': USER_PREFIX + userName,
            'SK': ACCOUNTS_PREFIX + accountID
        }
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)
    r2 = json_response("Deleted Item", response, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("DeleteItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

#endregion

#region /accountHoldings API
def get_account_holdings(event):
  print("get_account_holdings")
  try:

    qp = check_query_params(event)

    accountID = qp.get("accountID")

    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.query(
        TableName=os.environ.get("USERACCOUNTS_TABLE_NAME"),
        KeyConditionExpression='PK = :PK',
        ExpressionAttributeValues={
            ':PK': {'S': ACCOUNTS_PREFIX + accountID},
        }
    )
    print(response['Items'])
    items = response['Items']
    r2 = json_response("Holdings Info", items, 200)

    if not items:
      print("No items queried")
      error_response = json_response("Error", "Empty result", 404)
      return error_response
    
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def update_account_holdings(event):
  print("update_account_holdings")
  try:
    accountHoldingRequest = get_request_from_body(event)
    holdingUpdationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

    table = _get_table()

    response = table.update_item(
        Key={
            'PK': ACCOUNTS_PREFIX + accountHoldingRequest.accountID,
            'SK': ACC_HOLDING_PREFIX + accountHoldingRequest.instrument.lower()
        },
        UpdateExpression="set #quantity=:q, #unit_price=:u, #holding_update_time=:h",
        ExpressionAttributeNames={
            "#quantity": "quantity",
            "#unit_price": "unit_price",
            "#holding_update_time": "holding_update_time"
        },
        ExpressionAttributeValues={
            ":q": Decimal(str(accountHoldingRequest.quantity)),
            ":u": Decimal(str(accountHoldingRequest.unit_price)),
            ":h": holdingUpdationTime
        },
        ReturnValues="UPDATED_NEW"
    )
    r2 = json_response("Updated Item", accountHoldingRequest.__dict__, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("UpdateItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def create_account_holdings(event):
  print("create_account_holdings")

  try:
    accountHoldingsRequest = get_request_from_body(event)
    # accountHoldingsRequest = AccountHoldingRequest(accountHoldingsRequest)

    # Create the user account
    holdingCreationTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    print(accountHoldingsRequest)
    print(type(accountHoldingsRequest))
    accountID = ACCOUNTS_PREFIX + accountHoldingsRequest.accountID
    holdingID = HOLDING_PREFIX + accountHoldingsRequest.instrument.lower()
    accHoldingID = ACC_HOLDING_PREFIX + accountHoldingsRequest.instrument.lower()

    # dob = userProfileRequest.dob.strftime('%Y-%m-%d')
    item = {
        "PK": accountID,
        "SK": accHoldingID,
        "GSI1": holdingID,
        "quantity": Decimal(str(accountHoldingsRequest.quantity)),
        "unit_price": Decimal(str(accountHoldingsRequest.unit_price)),
        "holding_creation_time": holdingCreationTime
    }

    # Put item into the table.
    table = _get_table()
    response = table.put_item(Item=item)

    r2 = json_response("Holding Created", item, 200)
    print(r2)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def delete_account_holdings(event):
  print("delete_account_holdings")
  try:
    qp = check_query_params(event)

    accountID = qp.get("accountID")
    instrument = qp.get("instrument")

    table = _get_table()

    response = table.delete_item(
        Key={
            'PK': ACCOUNTS_PREFIX + accountID,
            'SK': ACC_HOLDING_PREFIX + instrument.lower()
        }
    )
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    print(status_code)
    r2 = json_response("Deleted Item", response, 200)

  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("DeleteItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

#endregion

#region /holdingInAccounts API
# TODO - add userName filter - means add userName when creating holding
def get_holding_in_accounts(event):
  print("get_holding_in_accounts")
  try:

    qp = check_query_params(event)

    instrument = qp.get("instrument")

    dynamodb_client = boto3.client('dynamodb')
    response = dynamodb_client.query(
        TableName=os.environ.get("USERACCOUNTS_TABLE_NAME"),
        IndexName=os.environ.get("USERACCOUNTS_TABLE_INDEX"),
        KeyConditionExpression='GSI1 = :GSI1 AND begins_with (SK, :SK)',
        ExpressionAttributeValues={
            ':GSI1': {'S': HOLDING_PREFIX + instrument.lower()},
            ':SK': {'S': ACC_HOLDING_PREFIX}
        }
    )
    print(response['Items'])
    items = response['Items']
    r2 = json_response("Holding in Accounts Info", items, 200)

    if not items:
      print("No items queried")
      error_response = json_response("Error", "Empty result", 404)
      return error_response
    
  except ClientError as e:
    print(e.response['Error']['Message'])
    raise e
  else:
    print("Insert succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))

  return r2

def create_holding_in_accounts(event):
  print("create_holding_in_accounts")

def update_holding_in_accounts(event):
  print("update_holding_in_accounts")

def delete_holding_in_accounts(event):
  print("delete_holding_in_accounts")

#endregion

def _get_table():
    table_name = os.environ.get("USERACCOUNTS_TABLE_NAME")
    return boto3.resource("dynamodb").Table(table_name)

def _get_index():
    index_name = os.environ.get("USERACCOUNTS_TABLE_INDEX")
    return index_name
    # return boto3.resource("dynamodb").Table(index_name)

'''
def processRequest(event):
  print(event)

  httpMethod = event['httpMethod']
  query_params = event['queryStringParameters']
  path_params = event['pathParameters']
  resource = event['resource']
  print(query_params)
  print(path_params)

  # Check if its for user, accounts or for holdings
  if resource == "/userProfile":
    print("User profile request")
    # process_user_profile_request(httpMethod, query_params)
    # process_user_profile_request(event)

  # use a dict switch for http methods
  # try using an enum for the different operations

  elif resource == "/userAccounts":
    print("User Accounts request")
  elif resource == "/accountHoldings":
    print("Accoun Holdings request")
  elif resource == "/holdingInAccounts":
    print(" Holdings In Accounts request")
  else:
    print("Unsupported route")
    raise Exception("Unsupported route: ", resource)

  if httpMethod == "GET":   
    # GET Method
    print("GET")

    if (query_params):
      print(query_params)
    else:
      print("Invalid request. No query params. Request either user, account or holdings information")
      raise Exception("Invalid request. No query params. Request either user, account or holdings information")

  elif httpMethod == "POST":
    print("POST")
    # POST /userProfile  - create user
    body = event['body']
    bodyD = json.loads(body)
    print (body)
    userProfileRequest = Dict2Class(bodyD)
    return create_user_profile(userProfileRequest)

    # POST /userAccounts  - create account
    # POST /accountHoldings?accountID={accountID}&holdingID={holdingID}   - create a holding in an account

  elif httpMethod == "PUT":
    print("Put")

  elif httpMethod == "DELETE":
    print("Delete")

  else:
    print("Invalid method request")
    raise Exception("Invalid method request")

'''

# TODO 
# Util functions refactor
#  - response - json fix - Internal Server Error - 502 bad Gateway even for successfull POSTs
#  - error response

