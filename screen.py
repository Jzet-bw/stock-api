from flask import Flask, request, jsonify
import pandas as pd
import traceback

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        max_price = float(request.args.get('price', 10000))
        print(f"▶ 受け取った max_price: {max_price}")

        df = pd.read_csv("dataG.csv", encoding="utf-8")
        print(f"▶ CSV 読み込み成功。行数: {len(df)}")

        # 列名調整（8列目と9列目が5日・25日移動平均乖離）
        df.columns.values[7] = '株価移動平均線乖離率(5日)'
        df.columns.values[8] = '株価移動平均線乖離率(25日)'

        required_cols = [
            'コード', '銘柄名', '市場', '現在値',
            'RSI(%)', '株価移動平均線乖離率(5日)',
            '株価移動平均線乖離率(25日)', '過去60日ボラティリティ(%)', 'ボリンジャーバンド'
        ]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"必要なカラムが見つかりません: {col}")

        df = df.dropna(subset=required_cols)
        df['現在値'] = df['現在値'].astype(float)
        df['RSI(%)'] = df['RSI(%)'].astype(float)
        df['株価移動平均線乖離率(5日)'] = df['株価移動平均線乖離率(5日)'].astype(float)
        df['株価移動平均線乖離率(25日)'] = df['株価移動平均線乖離率(25日)'].astype(float)
        df['過去60日ボラティリティ(%)'] = df['過去60日ボラティリティ(%)'].astype(float)
        df['ボリンジャーバンド'] = df['ボリンジャーバンド'].astype(float)

        # ゴールデンクロス判定列追加（5日 > 25日）
        df['GC'] = df['株価移動平均線乖離率(5日)'] > df['株価移動平均線乖離率(25日)']

        # ✅ フィルタ：価格条件のみ
        filtered = df[df['現在値'] <= max_price]

        print(f"▶ スクリーニング結果: {len(filtered)}件")

        results = []
        for _, row in filtered.iterrows():
            results.append({
                "code": str(row['コード']),
                "name": row['銘柄名'],
                "market": row['市場'],
                "price": row['現在値'],
                "rsi": row['RSI(%)'],
                "volatility": row['過去60日ボラティリティ(%)'],
                "ma5_disparity": row['株価移動平均線乖離率(5日)'],
                "ma25_disparity": row['株価移動平均線乖離率(25日)'],
                "bb_width": row['ボリンジャーバンド'],
                "gc": row['GC']
            })

        return jsonify({"status": "ok", "results": results})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/lookup")
def lookup():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"status": "error", "message": "symbol is required"}), 400

    code = symbol.replace(".T", "")  # "7203.T" → "7203"
    try:
        df = pd.read_csv("data.csv", encoding="utf-8")

        row = df[df["コード"].astype(str) == code]
        if row.empty:
            return jsonify({"status": "not_found", "name": ""})

        row = row.iloc[0]

        result = {
            "status": "ok",
            "name": row["銘柄名"],
            "rsi": float(row["RSI(%)"]),
            "ma5_disparity": float(row["株価移動平均線乖離率(%)"]),     # ← 正しい列名
            "ma25_disparity": float(row["株価移動平均線乖離率(%).1"]),  # ← 正しい列名
            "volatility": float(row["過去60日ボラティリティ(%)"]),
            "bb_width": float(row["ボリンジャーバンド"])
        }

        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/search_name', methods=['GET'])
def search_name():
    keyword = request.args.get('keyword', '')
    df = pd.read_csv("data.csv", encoding="utf-8")

    matched = df[df['銘柄名'].str.contains(keyword, na=False)]
    if matched.empty:
        return jsonify({"status": "not_found", "results": []})

    # 列の正確な対応
    required_cols = [
        'コード', '銘柄名',
        'RSI(%)',
        '株価移動平均線乖離率(%)',
        '株価移動平均線乖離率(%).1',
        '過去60日ボラティリティ(%)',
        'ボリンジャーバンド'
    ]
    for col in required_cols:
        if col not in matched.columns:
            return jsonify({"status": "error", "message": f"列 {col} が見つかりません"}), 500

    matched = matched.dropna(subset=required_cols)
    matched['RSI(%)'] = matched['RSI(%)'].astype(float)
    matched['株価移動平均線乖離率(%)'] = matched['株価移動平均線乖離率(%)'].astype(float)
    matched['株価移動平均線乖離率(%).1'] = matched['株価移動平均線乖離率(%).1'].astype(float)
    matched['過去60日ボラティリティ(%)'] = matched['過去60日ボラティリティ(%)'].astype(float)
    matched['ボリンジャーバンド'] = matched['ボリンジャーバンド'].astype(float)

    results = []
    for _, row in matched.iterrows():
        results.append({
            "コード": str(row['コード']),
            "銘柄名": row['銘柄名'],
            "rsi": row['RSI(%)'],
            "ma5_disparity": row['株価移動平均線乖離率(%)'],
            "ma25_disparity": row['株価移動平均線乖離率(%).1'],
            "volatility": row['過去60日ボラティリティ(%)'],
            "bb_width": row['ボリンジャーバンド']
        })

    return jsonify({"status": "ok", "results": results})
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)