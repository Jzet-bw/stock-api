from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        # クエリから最大株価を取得（デフォルトは10000）
        max_price = float(request.args.get('price', 10000))

        # CSVファイルの読み込み（同一ディレクトリに data.csv がある前提）
        df = pd.read_csv("data.csv", encoding="utf-8")

        # 欠損値を含む行を削除
        df = df.dropna(subset=[
            '現在値', 'RSI(%)', '過去60日ボラティリティ(%)', '株価移動平均線乖離率(%)',
            '5日移動平均', '25日移動平均'
        ])

        # ゴールデンクロス判定: 5日移動平均 > 25日移動平均
        df['ゴールデンクロス'] = df['5日移動平均'] > df['25日移動平均']

        # フィルタ条件の適用（ここでチューニング可能）
        filtered = df[
            (df['現在値'] <= max_price) &
            (df['RSI(%)'] < 65) &
            (df['過去60日ボラティリティ(%)'] < 40) &
            (df['株価移動平均線乖離率(%)'].abs() < 15) &
            (df['ゴールデンクロス'] == True)
        ]

        # 結果の整形
        results = []
        for _, row in filtered.iterrows():
            results.append({
                "code": str(row['コード']),
                "name": row['銘柄名'],
                "price": row['現在値'],
                "rsi": row['RSI(%)'],
                "volatility": row['過去60日ボラティリティ(%)'],
                "maDisparity": row['株価移動平均線乖離率(%)'],
                "goldenCross": row['ゴールデンクロス']
            })

        return jsonify({"status": "ok", "results": results})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)