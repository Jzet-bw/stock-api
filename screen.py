from flask import Flask, request, jsonify
import yfinance as yf
import pandas as pd

app = Flask(__name__)


@app.route('/screen', methods=['GET'])
def screen():
    try:
        max_price = float(request.args.get('price', 10000))

        # CSVファイルを読み込み（同じフォルダにあると仮定）
        df = pd.read_csv("data_j.csv", encoding="cp932")

        # コードと銘柄名を取得
        tickers = df[['コード', '銘柄名']].dropna().drop_duplicates()

        results = []

        for index, row in tickers.iterrows():
            code = str(row['コード']).zfill(4) + ".T"
            name = row['銘柄名']

            try:
                data = yf.Ticker(code)
                hist = data.history(period="1d")

                if hist.empty:
                    continue

                price = hist['Close'].iloc[-1]

                if price <= max_price:
                    results.append({
                        "code": code,
                        "name": name,
                        "price": round(price, 2)
                    })

            except Exception as e:
                print(f"Error processing {code}: {e}")
                continue

        return jsonify({"status": "ok", "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)