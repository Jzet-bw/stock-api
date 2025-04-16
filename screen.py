from flask import Flask, request, jsonify
import yfinance as yf
import os

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        max_price = float(request.args.get('price', 10000))

        # 一部の日本株を例示（本番ではもっと多く取得可能）
        tickers = ["7203.T", "9984.T", "6758.T", "9432.T"]
        result = []

        for code in tickers:
            data = yf.Ticker(code)
            hist = data.history(period="1d")
            if hist.empty:
                continue

            price = hist['Close'].iloc[-1]

            if price <= max_price:
                result.append({
                    "code": code,
                    "price": round(price, 2)
                })

        return jsonify({"status": "ok", "results": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Renderで必要
    app.run(host="0.0.0.0", port=port)