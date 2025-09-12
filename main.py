from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from stock_trade import stock_route
from stock_trade.demo_stock import process_stock_chunk, process_stock_chunk_ws

app = FastAPI()

app.include_router(stock_route.stock_router, prefix="/stock")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()   # 接受客户端连接
    try:
        while True:
            data = await websocket.receive_text()   # 接收文本消息
            if data is not None:
                await process_stock_chunk_ws(data, websocket)
            # await websocket.send_text(f"{response_data}")  # 发送响应
    except WebSocketDisconnect:  # 处理断开连接
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
