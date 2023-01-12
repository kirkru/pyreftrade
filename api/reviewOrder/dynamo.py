import os
import time
import json
import base64
from uuid import uuid4
import boto3
from boto3.dynamodb.conditions import Attr, Key

from datetime import datetime, timezone
from decimal import Decimal

from .models import ReviewOrderRequest #, SendOrderRequest
from .utils import logger, tracer

table = boto3.resource("dynamodb").Table(os.environ["REVIEWORDER_TABLE_NAME"])

class Error(Exception):
    pass

class ReviewOrderNotFoundError(Error):
    logger.info(Error)
    pass

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

@tracer.capture_method
def create_reviewOrder(reviewOrderRequest: ReviewOrderRequest) -> dict:
    logger.info("Creating ReviewOrder")

    # Create the reviewOrder for the user

    # createdTime = int(time.time())
    reviewOrderTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    # print(reviewOrderRequest)
    # print(type(reviewOrderRequest))
    # print(reviewOrderRequest.orderItems)
    # print(type(reviewOrderRequest.orderItems))
    
    # item = marshal_object(reviewOrderRequest)
    item = {
        "reviewOrderId": str(uuid4()),
        "userName": reviewOrderRequest.userName.lower(),
        "accountId": reviewOrderRequest.accountId,
        "reviewOrderTime": reviewOrderTime,
        "totalPrice": Decimal(str(reviewOrderRequest.totalPrice)),
        "orderItems": json.loads(json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]), parse_float=Decimal),
        # "orderItems": json.loads(json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]), parse_float=Decimal),
        # "orderItems": json.dumps([ob.__dict__ for ob in reviewOrderRequest.orderItems]),
    }

    # Put item into the table.
    table.put_item(Item=item)
    return {"reviewOrder": item}

@tracer.capture_method
def get_reviewOrder(userName: str) -> dict:
    logger.info("Listing ReviewOrders")
  
    # Get the reviewOrder from the table for userName.
    response = table.get_item(Key={"userName": userName.lower()})
    print(response)
    reviewOrderItem = response.get("Item")
    if not reviewOrderItem:
        raise ReviewOrderNotFoundError
    # HTTPException(status_code=404, detail=f"ReviewOrder for User: {userName} not found")
    return {"reviewOrder": reviewOrderItem}

@tracer.capture_method
def delete_reviewOrder(userName: str):
    logger.info("Deleting ReviewOrder")

    try:
        table.delete_item(
            Key={
                "userName": userName,
            },
            ConditionExpression=Attr("userName").exists(),
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        raise ReviewOrderNotFoundError

    return {"deleted_userName_reviewOrder": userName}


def prepareOrderPayload(reviewOrder):
  logger.info("prepareOrderPayload")

  try:
    totalPrice = Decimal('0.0')
    #  Convert to Object
    # objReviewOrder = DictObj(reviewOrder)
    objReviewOrder = reviewOrder

    # Calculate total price
    # for orderItem in objReviewOrder.orderItems:
    #   totalPrice = totalPrice + (orderItem.quantity * orderItem.price)

    for orderItem in objReviewOrder['reviewOrder']['orderItems']:
        totalPrice = totalPrice + (orderItem['quantity'] * orderItem['price'])

    print(totalPrice)

    totalPriceDict = {'totalPrice': totalPrice}
    reviewOrder['reviewOrder'].update(totalPriceDict)

    # setattr(objReviewOrder, "totalPrice" , totalPrice)

    # reviewOrder.totalPrice = totalPrice

    # copy all properties from reviewOrder into checkoutRequest

    # orderPayload.__dict__ = reviewOrder.__dict__.copy() 
    # return reviewOrder, totalPrice
    # return objReviewOrder.__dict__
    return reviewOrder

  except Exception as e:
      logger.info(e)
      raise e
      # print(traceback.format_exc())

  '''
    console.log("sendOrder");

  // expected request payload : { userName : vgt, attributes[firstName, lastName, email ..] 
  const checkoutRequest = JSON.parse(event.body);
  if (checkoutRequest == null || checkoutRequest.userName == null) {
    throw new Error(`userName should exist in checkoutRequest: "${checkoutRequest}"`);
  }  
  
  // 1- Get existing reviewOrder with items
  const reviewOrder = await getReviewOrder(checkoutRequest.userName);

  // 2- create an event json object with reviewOrder items, 
    // calculate totalprice, prepare order create json data to send ordering ms 
  var checkoutPayload = prepareOrderPayload(checkoutRequest, reviewOrder);

  // 3- publish an event to eventbridge - this will subscribe by order microservice and start ordering process.
  const publishedEvent = await publishSendOrderEvent(checkoutPayload);

  // 4- remove existing reviewOrder
  await deleteReviewOrder(checkoutRequest.userName);
  '''

def publishSendOrderEvent(orderPayload):
  logger.info("Publishing the sendOrder event with: ", orderPayload)
  # dictOrderPayload = orderPayload.__dict__
  try:
    logger.info("Before params")

    eventBusParams = {
                'Source':os.environ.get("EVENT_SOURCE"),
                'DetailType':os.environ.get("EVENT_DETAILTYPE"),
                'Detail':json.dumps(orderPayload, indent=4, cls=DecimalEncoder),
                # 'Detail':json.dumps(orderPayload),
                'EventBusName':os.environ.get("EVENT_BUSNAME")
            }

    logger.info("After params")

    client = boto3.client('events')

    response = client.put_events(
        Entries=[eventBusParams]
    )
    print("Sucess: Event Sent. Got response: {}", response)
    return response
  except Exception as e:
    print("Exception occured", e)
    raise Exception(status_code=500, detail=f"Exception occured while publishing order event")


def _encode(data: dict) -> str:
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")


def _decode(data: str) -> dict:
    json_string = base64.b64decode(data.encode("utf-8")).decode("utf-8")
    return json.loads(json_string)