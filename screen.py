from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)


@app.route('/screen', methods=['GET'])
def screen():
    try:
        max_price = float(request.args.get('price', 10000))

        tickers = ["7203.T", "9984.T", "6758.T", "9432.T"]  # �� �{���͑S����
        result = []

        for code in tickers:
            data = yf.Ticker(code)
            price = data.history(period="1d")['Close'].iloc[-1]

            if price <= max_price:
                result.append({
                    "code": code,
                    "price": round(price, 2)
                })

        return jsonify({"status": "ok", "results": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run()