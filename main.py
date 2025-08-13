from fastapi import FastAPI

from stock_trade import stock_route

app = FastAPI()

app.include_router(stock_route.stock_router, prefix="/stock")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
