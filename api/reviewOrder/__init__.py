from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import ExceptionMiddleware
from mangum import Mangum
from . import dynamo, models
from .router import LoggerRouteHandler
from .utils import tracer, logger, metrics, MetricUnit
import warnings
import os

'''
Request samples

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

'''

def _get_sys_level():
    sys_level = os.environ.get("SYS_LEVEL")
    return sys_level

api_root_path = "/" + _get_sys_level()

app = FastAPI(title="ReviewOrder API", version=1.0, root_path=api_root_path)
app.router.route_class = LoggerRouteHandler
app.add_middleware(ExceptionMiddleware, handlers=app.exception_handlers)


handler = Mangum(app)

#region Setup Op-excellence methods Tracing, Logging and Metrics, Correlation and Exception Handling

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

#endregion

@app.get("/")
def get_root():
    return {"message": "Root of ReviewOrder API"}

# @app.post("/reviewOrder", status_code=201, response_model=models.ReviewOrderResponse)
@app.post("/reviewOrder")
def create_reviewOrder(payload: models.ReviewOrderRequest):
  res = dynamo.create_reviewOrder(payload)
  metrics.add_metric(name="CreatedReviewOrder", unit=MetricUnit.Count, value=1)
  return res

@app.get("/get-reviewOrder/{userName}")
def get_reviewOrder(userName: str):
  logger.info("In the get_reviewOrder function")
  try:
    return dynamo.get_reviewOrder(userName)
  except dynamo.ReviewOrderNotFoundError:
    raise HTTPException(status_code=404, detail=f"No ReviewOrders found for user {userName}")

@app.delete("/delete-reviewOrder/{userName}")
def delete_reviewOrder(userName: str):
  try:
    dynamo.delete_reviewOrder(userName)
  except dynamo.ReviewOrderNotFoundError:
    raise HTTPException(status_code=404, detail=f"Review Order for user: {userName} not found")

@app.put("/sendOrder/{userName}")
def sendOrder(userName: str):
  # TODO - Add try catch

  logger.info("1 - Getting existing reviewOrder with items")

  reviewOrder = dynamo.get_reviewOrder(userName)

  print("Review Order: ", reviewOrder)

  logger.info("2 - create an event json object with reviewOrder items")

  # reviewOrderRequest = ReviewOrderRequest.from_dict(reviewOrder)
  # orderPayload, totalPrice = prepareOrderPayload(reviewOrder)
  orderPayload = dynamo.prepareOrderPayload(reviewOrder)

  print(orderPayload)

  # print(totalPrice)

  logger.info("3 - publish an event to EventBridge")
  publishedEvent = dynamo.publishSendOrderEvent(orderPayload)

  # TODO - update delete reviewOrder with accountID

  logger.info("4 - remove existing reviewOrder")
  dynamo.delete_reviewOrder(userName)

  return {"Success": "Sent order to the event bus"}

@app.get("/fail")
def fail():
    some_dict = {}
    return some_dict["missing_key"]
