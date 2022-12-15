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
    return {"message": "Root of Instruments API"}


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
