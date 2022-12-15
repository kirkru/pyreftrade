import os
import time
import json
import base64
from uuid import uuid4
import boto3
from boto3.dynamodb.conditions import Attr, Key

from .models import InstrumentRequest, UpdateInstrument
from .utils import logger, tracer

table = boto3.resource("dynamodb").Table(os.environ["REVIEWORDER_TABLE_NAME"])
# sector_index = os.environ["INSTRUMENTS_SECTOR_INDEX"]

class Error(Exception):
    pass

class InstrumentNotFoundError(Error):
    pass

class SectorNotFoundError(Error):
    pass

@tracer.capture_method
def create_instrument(instrumentRequest: InstrumentRequest) -> dict:
    logger.info("Creating Instrument")

    created_time = int(time.time())
    item = {
        "ticker": instrumentRequest.ticker.lower(),
        "created_time": created_time,
        "company": instrumentRequest.company,
        "sector": instrumentRequest.sector.lower(),
        "description": instrumentRequest.description,
        # "current_price": instrumentRequest.current_price,
        "type": instrumentRequest.type
        # "ttl": int(created_time + 86400),  # Expire after 24 hours.
    }

    # Put it into the table.
    table.put_item(Item=item)
    return item

@tracer.capture_method
def get_instrument(ticker: str) -> dict:
    logger.info("Getting Instrument")

    res = table.get_item(
        Key={
            "ticker": ticker.lower(),
        },
    )

    item = res.get("Item")
    if not item:
        raise InstrumentNotFoundError

    return item

@tracer.capture_method
def get_sectors() -> dict:
    logger.info("Getting Sectors")

    response = table.scan(
        # IndexName="sector-index",
        ProjectionExpression="sector",
        # KeyConditionExpression=Key("sector").eq(sector),
        # ScanIndexForward=False,
        # Limit=10,
    )
    sectors = response.get("Items")
    if not sectors:
        raise SectorNotFoundError

    return {"sectors": sectors}

@tracer.capture_method

@tracer.capture_method
def list_instruments_in_sector(sector: str, next_token: str = None) -> dict:
    logger.info("Listing Instruments In Sector")
    try:
            
        scan_args = {
            "Limit": 10,
        }

        if next_token:
            scan_args["ExclusiveStartKey"] = _decode(next_token)

        res = table.query(
            IndexName=sector_index,
            KeyConditionExpression=Key("sector").eq(sector.lower()),
            ScanIndexForward=False,
            Limit=10,
        )
        logger.info(res)
        response = {"Instruments": res.get("Items")}

        if "LastEvaluatedKey" in res:
            response["next_token"] = _encode(res["LastEvaluatedKey"])

        return response

    except Exception as e:
        print("Error Occured while processing request: ", e)

@tracer.capture_method
def update_instrument(ticker: str, updateInstrument: UpdateInstrument) -> dict:
    expr = []
    attr_values = {}
    attr_names = {}

    if updateInstrument.company is not None:
        expr.append("#C=:c")
        attr_values[":c"] = updateInstrument.company
        attr_names["#C"] = "company"

    if updateInstrument.description is not None:
        expr.append("#D=:d")
        attr_values[":d"] = updateInstrument.description
        attr_names["#D"] = "description"

    if updateInstrument.sector is not None:
        expr.append("#S=:s")
        attr_values[":s"] = updateInstrument.sector
        attr_names["#S"] = "sector"

    if updateInstrument.type is not None:
        expr.append("#T=:t")
        attr_values[":t"] = updateInstrument.type
        attr_names["#T"] = "type"

    if not expr:
        logger.info("No fields to update")
        return

    logger.info("Updating Instrument", updateInstrument, attr_values, attr_names)
    try:
        response = table.update_item(
            Key={
                "ticker": ticker,
            },
            UpdateExpression=f"set {', '.join(expr)}",
            ExpressionAttributeValues=attr_values,
            ExpressionAttributeNames=attr_names,
            ConditionExpression=Attr("ticker").exists(),
        )
        
        r2 = {"Updated Item", ticker}
        # r2 = json_response("Updated Item", userProfileRequest.__dict__, 200)

    # except ClientError as e:
    #     print(e.response['Error']['Message'])
    #     raise e
    # else:
    #     print("UpdateItem succeeded:")
    #     print(json.dumps(response, indent=4, cls=DecimalEncoder))
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        raise InstrumentNotFoundError

@tracer.capture_method
def list_instruments(next_token: str = None) -> dict:
    logger.info("Listing Instruments")
    try:
            
        scan_args = {
            "Limit": 10,
        }

        if next_token:
            scan_args["ExclusiveStartKey"] = _decode(next_token)

        res = table.scan()
        # res = table.scan(**scan_args)
        response = {"Instruments": res["Items"]}
        # response = {"Instruments": res.get("Items")}

        if "LastEvaluatedKey" in res:
            response["next_token"] = _encode(res["LastEvaluatedKey"])

        return response

    except Exception as e:
        print("Error Occured while processing request: ", e)

@tracer.capture_method
def delete_instrument(ticker: str):
    logger.info("Deleting Instrument")

    try:
        table.delete_item(
            Key={
                "ticker": ticker,
            },
            ConditionExpression=Attr("ticker").exists(),
        )
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        raise InstrumentNotFoundError

def _encode(data: dict) -> str:
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode("utf-8")).decode("utf-8")


def _decode(data: str) -> dict:
    json_string = base64.b64decode(data.encode("utf-8")).decode("utf-8")
    return json.loads(json_string)