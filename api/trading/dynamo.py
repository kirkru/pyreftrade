import os
import time
import json
import base64
from uuid import uuid4
import boto3
from boto3.dynamodb.conditions import Attr, Key

from .models import TradeRequest
from .utils import logger, tracer

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from decimal import Decimal


table = boto3.resource("dynamodb").Table(os.environ["TRADING_TABLE_NAME"])

class Error(Exception):
    pass

class TradeNotFoundError(Error):
    logger.info(Error)
    pass


# Process Trade
@tracer.capture_method
def process_trade(eventDetailDict):
# def process_trade(tradeRequest: TradeRequest):
    logger.info("Processing Trade Request")

    '''
    
    {'reviewOrderTime': '2022-10-19T00:37:32.664760+00:00', 'userName': 'kir', 'totalPrice': '2600.0', 'orderItems': [{'symbolId': 'AAPL', 'symbolName': 'Apple Inc.', 'quantity': '4', 'price': '200'}, {'symbolId': 'XOM', 'symbolName': 'Exxon Mobil Inc.', 'quantity': '2', 'price': '900'}]}

    '''

    try: 
        tradeProcessedTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        # parsing reviewOrderId
        # reviewOrderId = datetime.fromisoformat(eventDetailDict["reviewOrderId"])
    #     item = {
    #         "accountId": tradeRequest.accountId,
    #         "tradeId": str(uuid4()),
    #         "tradeProcessedTime": tradeProcessedTime,
    #         "userName": tradeRequest.userName,
    #         "reviewOrderTime": tradeRequest.reviewOrderTime,
    #         "reviewOrderId": tradeRequest.reviewOrderId,
    #         "totalPrice": Decimal(str(tradeRequest.totalPrice)),
    #         "tradeItems": tradeRequest.tradeItems,
    #    }

        item = {
            "accountId": eventDetailDict["accountId"],
            "tradeId": str(uuid4()),
            "tradeProcessedTime": tradeProcessedTime,
            "userName": eventDetailDict["userName"],
            "reviewOrderTime": eventDetailDict["reviewOrderTime"],
            "reviewOrderId": eventDetailDict["reviewOrderId"],
            "totalPrice": Decimal(str(eventDetailDict["totalPrice"])),
            "tradeItems": eventDetailDict["orderItems"],
            # "orderItems": [ob.__dict__ for ob in reviewOrderRequest.orderItems],
            # "orderItems": json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]),
        }
    except Exception as e:
            print("Error Occured while processing Trade: ", e)

    # Put it into the table.
    table.put_item(Item=item)
    return {"trade": item}

# Get Trade information
@tracer.capture_method
def get_trades(accountId: str, dateRange: str) -> dict:
    try:
            
        # Get the trades from the table for accountId.
        dateQuery = switch(dateRange)

        dynamodb_client = boto3.client('dynamodb')
        response = dynamodb_client.query(
            TableName=os.environ.get("TRADING_TABLE_NAME"),
            KeyConditionExpression='accountId = :accountId AND tradeProcessedTime > :dateQuery',
            ExpressionAttributeValues={
                ':accountId': {'S': accountId},
                ':dateQuery': {'S': dateQuery}
            }
        )
        print(response['Items'])

        # query single item using boto3 resource
        # table = _get_table()
        # response = table.get_item(Key={"accountId": accountId, "tradeProcessedTime": })
        # print(response)
        # item = response.get("Item")
        # print(item)

        if not response['Items']:
            raise TradeNotFoundError
        # Exception(f"Trades for Account: {accountId} in the given date range: {dateRange}, not found")
        return response['Items']

    except Exception as e:
        print("Exception occured", e)
        raise Exception(status_code=500, detail=f"Trades for Account: {accountId} in the given date range: {dateRange}, not found")


# Get the date range for performing query
def switch(dateRange: str):

  if not dateRange:
    dateRange = ''
  now = datetime.today()
  if dateRange == "1w":   
      # 1 week
      dateQuery = now - relativedelta(days=7)
  elif dateRange == "1m":
      # 1 month
      dateQuery = now - relativedelta(months=1)
  elif dateRange == "3m":
  # 3 months
      dateQuery = now - relativedelta(months=3)
  elif dateRange == "6m":
  # 6 months
      dateQuery = now - relativedelta(months=6)
  elif dateRange == "1y":
  # 1 year
      dateQuery = now - relativedelta(years=1)
  else:
      # default to yesterday 
      dateQuery = now - relativedelta(days=1)

  dateQuery = dateQuery.strftime('%Y-%m-%d')
  print(dateQuery)
  return(dateQuery)

def _encode(data: dict) -> str:
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")


def _decode(data: str) -> dict:
    json_string = base64.b64decode(data.encode("utf-8")).decode("utf-8")
    return json.loads(json_string)