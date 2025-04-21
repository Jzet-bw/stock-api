from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        # 金額の取得（例: /screen?price=2000）
        max_price = float(request.args.get('price', 10000))

        # CSVの読み込み（Shift_JIS / CP932対応）
        df = pd.read_csv("screen_data.csv", encoding="cp932")

        # 必要な列がすべてあるか確認
        required_columns = [
            "コード", "銘柄名", "現在値", "株価移動平均線乖離率(%)",
            "出来高増加率(倍)", "過去60日ボラティリティ(%)", "RSI(%)"
        ]
        for col in required_columns:
            if col not in df.columns:
                return jsonify({"status": "error", "message": f"CSVに'{col}'列が見つかりません"}), 400

        # スクリーニング条件を適用
        filtered = df[
            (df["現在値"] <= max_price) &
            (df["RSI(%)"] >= 40) & (df["RSI(%)"] <= 60) &
            (df["過去60日ボラティリティ(%)"] <= 5) &
            (df["株価移動平均線乖離率(%)"] >= -5) & (df["株価移動平均線乖離率(%)"] <= 5) &
            (df["出来高増加率(倍)"] >= 1.5)
        ]

        # 結果を整形
        results = filtered[["コード", "銘柄名", "現在値", "RSI(%)", "過去60日ボラティリティ(%)"]].to_dict(orient="records")

        return jsonify({
            "status": "ok",
            "count": len(results),
            "results": results
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
