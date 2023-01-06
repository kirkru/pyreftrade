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
    pass

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
        "reviewOrderId": str(uuid.uuid4()),
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


def _encode(data: dict) -> str:
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")


def _decode(data: str) -> dict:
    json_string = base64.b64decode(data.encode("utf-8")).decode("utf-8")
    return json.loads(json_string)