from orderbook import OrderBook
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import json
import uvicorn
from decimal import Decimal

order_books = {}  # Dictionary to store multiple order books, keyed by symbol
app = FastAPI()

@app.post("/api/register_order")
def register_order(payload: str = Form(...)):
    try:
        payload_json = json.loads(payload)
        symbol = "%s_%s" % (payload_json["baseAsset"], payload_json["quoteAsset"])

        if symbol not in order_books:
            order_books[symbol] = OrderBook()

        order_book = order_books[symbol]

        _order = {
            'type' : 'limit',
            'trade_id' : payload_json['account'],
            'account': payload_json['account'],
            'price' : Decimal(payload_json['price']),
            'quantity' : Decimal(payload_json['quantity']),
            'side' : payload_json['side'],
            'baseAsset' : payload_json['baseAsset'],
            'quoteAsset' : payload_json['quoteAsset']
        }
        trades, order = order_book.process_order(_order, False, False)

        converted_trades = []
        for trade in trades:
            # [trade_id, side, head_order.order_id, new_book_quantity]
            party1 = [
                trade['party1'][0],
                trade['party1'][1],
                int(trade['party1'][2]) if trade['party1'][2] is not None else None,
                float(trade['party1'][3]) if trade['party1'][3] is not None else None
            ]
            party2 = [
                trade['party2'][0],
                trade['party2'][1],
                int(trade['party2'][2]) if trade['party2'][2] is not None else None,
                float(trade['party2'][3]) if trade['party2'][3] is not None else None
            ]

            converted_trade = {
                'timestamp': int(trade['timestamp']),
                'price': float(trade['price']),
                'quantity': float(trade['quantity']),
                'time': int(trade['time']),
                'party1': party1,
                'party2': party2,
            }
            converted_trades.append(converted_trade)

        if order is None:
            order = _order.copy()
            order['order_id'] = None

        # Convert order to a serializable format
        order_dict = {
            'order_id': int(order['order_id']) if order['order_id'] is not None else None,
            'account': order['account'],
            'price': float(order['price']),
            'quantity': float(order['quantity']),
            'side': order['side'],
            'baseAsset': order['baseAsset'],
            'quoteAsset': order['quoteAsset'],
            # 'type': order['type'],
            'trade_id': order['trade_id'],
            'trades': converted_trades
        }

        return JSONResponse(content={
            "message": "Order registered successfully",
            "order": order_dict
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cancel_order")
def cancel_order(payload: str = Form(...)):
    try:
        payload_json = json.loads(payload)
        order_id = payload_json['orderId']
        side = payload_json['side']
        symbol = "%s_%s" % (payload_json["baseAsset"], payload_json["quoteAsset"])

        order_book = order_books[symbol]
        order_book.cancel_order(side, order_id)

        # Convert order to a serializable format
        order_dict = {
            'order_id': int(order_id),
            'side': side,
            'baseAsset': payload_json["baseAsset"],
            'quoteAsset': payload_json["quoteAsset"],
        }

        return JSONResponse(content={
            "message": "Order cancelled successfully",
            "order": order_dict
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orderbook")
def get_orderbook(payload: str = Form(...)):
    try:
        payload_json = json.loads(payload)
        symbol = payload_json['symbol']

        if symbol not in order_books:
            raise HTTPException(status_code=404, detail="Order book not found")

        order_book = order_books[symbol]

        return order_book.get_orderbook(payload_json['symbol'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/get_best_order")
def get_best_order(payload: str = Form(...)):
    try:
        payload_json = json.loads(payload)
        symbol = "%s_%s" % (payload_json["baseAsset"], payload_json["quoteAsset"])
        side = payload_json['side']

        if symbol not in order_books:
            raise HTTPException(status_code=404, detail="Order book not found")

        order_book = order_books[symbol]

        if side == 'bid':
            price = order_book.get_best_bid()
            price_list = order_book.bids.price_map[price]
        else:
            price = order_book.get_best_ask()
            price_list = order_book.asks.price_map[price]

        current_order = price_list.head_order

        order_dict = {
            'order_id': int(current_order.order_id),
            'account': current_order.account,
            'price': float(current_order.price),
            'quantity': float(current_order.quantity),
            'side': current_order.side,
            'baseAsset': current_order.baseAsset,
            'quoteAsset': current_order.quoteAsset,
            'trade_id': current_order.trade_id,
        }

        return JSONResponse(content={
            "message": "Best order retrieved successfully",
            "order": order_dict
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
