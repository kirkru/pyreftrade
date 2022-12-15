from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import ExceptionMiddleware
from mangum import Mangum
from . import dynamo, models
from .router import LoggerRouteHandler
from .utils import tracer, logger, metrics, MetricUnit
import warnings
import os


# TODO
# Add GET API 
# Test DynamoDB model
# Use DAX?

# Integration
# Test end to end - including accounts API
# Try streamlit or dev.to - https://dev.to/aws-builders/secure-your-api-gateway-apis-with-auth0-a4o

#  API requests test

# GET
# https://o009nx09rl.execute-api.us-west-2.amazonaws.com/eng/trade?accountId=acc123&dateRange=1m
# https://o009nx09rl.execute-api.us-west-2.amazonaws.com/eng/trade?accountId=acc123

# POST from EventBus, SQS

#  GET 
def handler(event, context):
  print("Event:", event)
  print("Context:", context)

  # Sample event
  '''
  # synchronous
  event = {'resource': '/trade', 'path': '/trade', 'httpMethod': 'GET', 'headers': {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9', 'CloudFront-Forwarded-Proto': 'https', 'CloudFront-Is-Desktop-Viewer': 'true', 'CloudFront-Is-Mobile-Viewer': 'false', 'CloudFront-Is-SmartTV-Viewer': 'false', 'CloudFront-Is-Tablet-Viewer': 'false', 'CloudFront-Viewer-ASN': '3356', 'CloudFront-Viewer-Country': 'US', 'Cookie': 'awsccc=eyJlIjoxLCJwIjoxLCJmIjoxLCJhIjoxLCJpIjoiMTRiM2NlMmMtNWQ5Zi00NDcwLTk0Y2MtMWQxOTE0YmY3Njk2IiwidiI6IjEifQ==', 'Host': 'f1q7j05929.execute-api.us-west-2.amazonaws.com', 'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"macOS"', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'Via': '2.0 48fa2d8b9525abe889eff7ccc8591f7e.cloudfront.net (CloudFront)', 'X-Amz-Cf-Id': 'iGgt0K25UwH5rsrVjqIKQ8Tr5bTimgc0G1YVABs3iFjK7PZIZYaXiA==', 'X-Amzn-Trace-Id': 'Root=1-634f17aa-26a3e3516e04451c45965a85', 'X-Forwarded-For': '4.28.107.176, 15.158.63.4', 'X-Forwarded-Port': '443', 'X-Forwarded-Proto': 'https'}, 'multiValueHeaders': {'Accept': ['text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'], 'Accept-Encoding': ['gzip, deflate, br'], 'Accept-Language': ['en-US,en;q=0.9'], 'CloudFront-Forwarded-Proto': ['https'], 'CloudFront-Is-Desktop-Viewer': ['true'], 'CloudFront-Is-Mobile-Viewer': ['false'], 'CloudFront-Is-SmartTV-Viewer': ['false'], 'CloudFront-Is-Tablet-Viewer': ['false'], 'CloudFront-Viewer-ASN': ['3356'], 'CloudFront-Viewer-Country': ['US'], 'Cookie': ['awsccc=eyJlIjoxLCJwIjoxLCJmIjoxLCJhIjoxLCJpIjoiMTRiM2NlMmMtNWQ5Zi00NDcwLTk0Y2MtMWQxOTE0YmY3Njk2IiwidiI6IjEifQ=='], 'Host': ['f1q7j05929.execute-api.us-west-2.amazonaws.com'], 'sec-ch-ua': ['"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"'], 'sec-ch-ua-mobile': ['?0'], 'sec-ch-ua-platform': ['"macOS"'], 'sec-fetch-dest': ['document'], 'sec-fetch-mode': ['navigate'], 'sec-fetch-site': ['none'], 'sec-fetch-user': ['?1'], 'upgrade-insecure-requests': ['1'], 'User-Agent': ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'], 'Via': ['2.0 48fa2d8b9525abe889eff7ccc8591f7e.cloudfront.net (CloudFront)'], 'X-Amz-Cf-Id': ['iGgt0K25UwH5rsrVjqIKQ8Tr5bTimgc0G1YVABs3iFjK7PZIZYaXiA=='], 'X-Amzn-Trace-Id': ['Root=1-634f17aa-26a3e3516e04451c45965a85'], 'X-Forwarded-For': ['4.28.107.176, 15.158.63.4'], 'X-Forwarded-Port': ['443'], 'X-Forwarded-Proto': ['https']}, 'queryStringParameters': None, 'multiValueQueryStringParameters': None, 'pathParameters': None, 'stageVariables': None, 'requestContext': {'resourceId': 'cbv1jx', 'resourcePath': '/trade', 'httpMethod': 'GET', 'extendedRequestId': 'aOCiqEIPvHcFvYw=', 'requestTime': '18/Oct/2022:21:16:26 +0000', 'path': '/eng/trade', 'accountId': '103384195692', 'protocol': 'HTTP/1.1', 'stage': 'eng', 'domainPrefix': 'f1q7j05929', 'requestTimeEpoch': 1666127786425, 'requestId': '03ce132c-567e-4173-893d-036d574f9c67', 'identity': {'cognitoIdentityPoolId': None, 'accountId': None, 'cognitoIdentityId': None, 'caller': None, 'sourceIp': '4.29.107.56', 'principalOrgId': None, 'accessKey': None, 'cognitoAuthenticationType': None, 'cognitoAuthenticationProvider': None, 'userArn': None, 'userAgent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36', 'user': None}, 'domainName': 'f1q7kklj929.e-api.us-west-2.amazonaws.com', 'apiId': 'f1q7j05929'}, 'body': None, 'isBase64Encoded': False}

  # asynchronous
  event2 = {'Records': [{'messageId': '136026a4-4d3c-4e75-a5ce-4319bb8aabd5', 'receiptHandle': 'AQEBPB5qEpe28t0magigWDok1p+TGnL7wrleNV6OHh4qeAi2/ZsAlx25qjbrYHVxSxfHNBKPG6n+W6Dqdc+knM2J6V0AA4KIfhR22zL9YKhh/dpKom44jeAw7gMLRqsz8c3wva70vQQndFM3jzKFA39xSldqR7YmNCgP4p4dURUOWllCExG2fouv3OMmZ8eUEarPYenktCK440z/5GEIByFBvUrz7wfyDtVvSYI5J5nsVciIvUMB0NbwcjzB5dKTYXQg3LKupjqvgMyKXDDpbLpee/AWyZrAvgr4exaViQulnwImoJFQ+U1HGIgt4fbMUncDdd8X5aaYWSVPZORaMml2UV7BgFb952zOQKz687rLB6K6BHmcMGFtuc1ygmv25f5VZXBr0V6nI8ElnnKffz1ZDQ==', 'body': '{"version":"0","id":"0e5ff78d-42de-a0d5-d023-b777c4cb0f86","detail-type":"tr_SendOrder","source":"com.vgt.reviewOrder.sendOrder","account":"103384195692","time":"2022-10-17T22:56:59Z","region":"us-west-2","resources":[],"detail":{"username":"tester","total":"1000"}}', 'attributes': {'ApproximateReceiveCount': '1', 'SentTimestamp': '1666047420059', 'SenderId': 'AIDAIE6VAXUQU2DKHA7DK', 'ApproximateFirstReceiveTimestamp': '1666047420067'}, 'messageAttributes': {}, 'md5OfBody': '450b09b1841e7a776459976f1eaff02f', 'eventSource': 'aws:sqs', 'eventSourceARN': 'arn:aws:sqs:us-west-2:1312xyz:tr_OrderQueue', 'awsRegion': 'us-west-2'}]}
  '''

  try :
      # Check if it's an api gateway invocation
      hm = event['httpMethod'] # this will throw a KeyError if its empty, i.e in the case of an event based invocation
      print(hm)
      return apiGatewayInvocation(event)

  except KeyError as ke:
      #  Seems to be an asynchronous invocation
      print("key error", ke)
      # e2m = json.loads(event2)
      try:
        body = event['Records'][0]['body']
        print (body)
        bodyD = json.loads(body)
        detail_type = bodyD['detail-type']
        print(detail_type)
        if (detail_type == 'tr_SendOrder'):
          print ("Trade Request")
          # This was invoked from the EventBride and SQS queue...
          eventBridgeInvocation(bodyD['detail'])
      except Exception as e:
        print("Error Occured while processing non http request: ", e)


# Asynchronous invocation
def eventBridgeInvocation(eventDetailDict):
  print ("Event Bridge invocation")
  # Process the Trade
  processTrade(eventDetailDict)


# Process Trade request
def processTrade(eventDetailDict):
  print("Process Trade for: ", eventDetailDict)
  '''
  
  {'reviewOrderTime': '2022-10-19T00:37:32.664760+00:00', 'userName': 'kir', 'totalPrice': '2600.0', 'orderItems': [{'symbolId': 'AAPL', 'symbolName': 'Apple Inc.', 'quantity': '4', 'price': '200'}, {'symbolId': 'XOM', 'symbolName': 'Exxon Mobil Inc.', 'quantity': '2', 'price': '900'}]}

  '''

  try: 
    tradeProcessedTime = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    # parsing reviewOrderId
    # reviewOrderId = datetime.fromisoformat(eventDetailDict["reviewOrderId"])
    item = {
        "accountId": eventDetailDict["accountId"],
        "tradeId": str(uuid.uuid4()),
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
  table = _get_table()
  table.put_item(Item=item)
  return {"trade": item}


# Synchronous invocation
def apiGatewayInvocation(event):
  print ("API Gateway invocation")
  query_params = event['queryStringParameters']

  print(query_params)

  try:

    # if (query_params is not None):
    if (query_params):
      # tradeId = query_params.get('tradeId')
      accountId = query_params.get('accountId')
      dateRange = query_params.get('dateRange')
      
      if not accountId:
        print("Invalid arguments")
        errorResponse =  {
          'statusCode': 404,
          "headers": {
            "Content-Type": "application/json"
          },
          'body': json.dumps({
              "message": "Invalid parameters were passed."
          })
        }
        return errorResponse

      # GET /trade?accountID=acc# // defaults to trades since yesterday
      # GET /trade?accountID=acc#&dateRange=1w,1m,3m,6m,1y 
      items = get_trades(accountId, dateRange)

      response = {
          "statusCode": 200,
          "headers": {
            "Content-Type": "application/json"
          },
          "body": json.dumps(items)
      }
      print(response)
      return response

      # return {
      #     'TradeInfo': response
      #     # 'body': json.dumps(event)
      # }
      # return {'message' : json.dumps(path_params)}

    else:
      print("No query params")
      return {
          'statusCode': 404,
          "headers": {
            "Content-Type": "application/json"
          },
          'body': json.dumps({
            'message': 'No parameters were passed'
            }
          )
      }
  except Exception as ex:
    print("Error Occured while obtaining Trade information: ", ex)
    return {
          'statusCode': 404,
          "headers": {
            "Content-Type": "application/json"
          },
          'body': json.dumps({
            'message': "Error Occured while obtaining Trade information"
          })
    }


# Get Trade information
def get_trades(accountId: str, dateRange: str):
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
        raise HTTPException(status_code=404, detail=f"Trades for Account: {accountId} in the given date range: {dateRange}, not found")
    return response['Items']


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


'''
Request samples
{
  "ticker": "QQQ",
  "company": "Tech ETF",
  "sector": "Technology",
  "description": "ETF for tech",
  "type": "stock"
}

{
  "ticker": "XLE",
  "company": "Energy ETF",
  "sector": "Energy",
  "description": "ETF for energy",
  "type": "stock"
}
'''

def _get_sys_level():
    sys_level = os.environ.get("SYS_LEVEL")
    return sys_level

api_root_path = "/" + _get_sys_level()

app = FastAPI(title="Instruments API", version=1.0, root_path=api_root_path)
# app = FastAPI(title="Instruments API", version=1.0, root_path="/eng")
app.router.route_class = LoggerRouteHandler
app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)


handler = Mangum(app)

# Add tracing
handler.__name__ = "handler"  # tracer requires __name__ to be set
handler = tracer.capture_lambda_handler(handler)
# Add logging
handler = logger.inject_lambda_context(handler, clear_state=True)
# Add metrics last to properly flush metrics.
warnings.filterwarnings("ignore", "No metrics to publish*")
handler = metrics.log_metrics(handler, capture_cold_start_metric=True)

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    # Get correlation id from X-Correlation-Id header
    corr_id = request.headers.get("x-correlation-id")
    if not corr_id:
        # If empty, use request id from aws context
        corr_id = request.scope["aws.context"].aws_request_id

    # Add correlation id to logs
    logger.set_correlation_id(corr_id)

    # Add correlation id to traces
    tracer.put_annotation(key="correlation_id", value=corr_id)

    response = await call_next(request)

    # Return correlation header in response
    response.headers["X-Correlation-Id"] = corr_id
    return response

@app.exception_handler(Exception)
async def unhandled_exception_handler(request, err):
    logger.exception("Unhandled exception")
    metrics.add_metric(name="UnhandledExceptions", unit=MetricUnit.Count, value=1)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/")
def get_root():
    return {"message": "Root of Trading API"}


@app.get("/instruments", response_model=models.InstrumentListResponse)
def list_instruments(next_token: str = None):
    return dynamo.list_instruments(next_token)

@app.get("/instruments/{ticker}", response_model=models.InstrumentResponse)
def get_instrument(ticker: str):
    # Get the instrument from the table.
    try:
        return dynamo.get_instrument(ticker)
    except dynamo.InstrumentNotFoundError:
        raise HTTPException(status_code=404, detail="Instrument: {ticker} not found")

@app.post("/instruments", status_code=201, response_model=models.InstrumentResponse)
# @metrics.log_metrics
def create_instrument(payload: models.InstrumentRequest):
    res = dynamo.create_instrument(payload)
    metrics.add_metric(name="CreatedInstruments", unit=MetricUnit.Count, value=1)
    return res

@app.patch("/instruments/{ticker}", status_code=204)
def update_instrument(ticker, payload: models.UpdateInstrument):
    try:
        return dynamo.update_instrument(ticker, payload)
    except dynamo.InstrumentNotFoundError:
        raise HTTPException(status_code=404, detail="Pet not found")

@app.get("/instruments/sectors/")
def get_sectors():
    # List the sectors from the table, using the sector index.
    try:
        return dynamo.get_sectors()
    except dynamo.SectorNotFoundError:
        raise HTTPException(status_code=404, detail="Sectors not found")

@app.get("/instruments/sectors/{sector}")
# @app.get("/instruments/sectors/{sector}", response_model=models.InstrumentListResponse)
def list_instruments_in_sector(sector: str, next_token: str = None):
    # List the top N instruments from the table, using the sector index.
    logger.info("In the listing functin")
    try:
        return dynamo.list_instruments_in_sector(sector, next_token)
    except dynamo.InstrumentNotFoundError:
        raise HTTPException(status_code=404, detail="No Instruments found in Sector {sector}")


@app.delete("/instruments/{ticker}", status_code=204)
def delete_instrument(ticker: str):
    try:
        dynamo.delete_instrument(ticker)
    except dynamo.InstrumentNotFoundError:
        raise HTTPException(status_code=404, detail="Instrument: {ticker} not found")


@app.get("/fail")
def fail():
    some_dict = {}
    return some_dict["missing_key"]
