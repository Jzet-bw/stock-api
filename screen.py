from flask import Flask, request, jsonify
import pandas as pd
import traceback

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        max_price = float(request.args.get('price', 10000))
        print(f"▶ 受け取った max_price: {max_price}")

        # CSVファイル読み込み（同じフォルダに data.csv がある必要）
        df = pd.read_csv("data.csv", encoding="utf-8")

        print(f"▶ CSV 読み込み成功。行数: {len(df)}")

        # 列名調整（8列目と9列目が5日・25日移動平均乖離）
        df.columns.values[7] = '株価移動平均線乖離率(5日)'
        df.columns.values[8] = '株価移動平均線乖離率(25日)'

        # 必須列が存在するか確認
        required_cols = [
            'コード', '銘柄名', '市場', '現在値',
            'RSI(%)', '株価移動平均線乖離率(5日)',
            '株価移動平均線乖離率(25日)', '過去60日ボラティリティ(%)'
        ]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"必要なカラムが見つかりません: {col}")

        # NaN除去 & 型変換
        df = df.dropna(subset=required_cols)
        df['現在値'] = df['現在値'].astype(float)
        df['RSI(%)'] = df['RSI(%)'].astype(float)
        df['株価移動平均線乖離率(5日)'] = df['株価移動平均線乖離率(5日)'].astype(float)
        df['株価移動平均線乖離率(25日)'] = df['株価移動平均線乖離率(25日)'].astype(float)
        df['過去60日ボラティリティ(%)'] = df['過去60日ボラティリティ(%)'].astype(float)

        # ゴールデンクロス判定列の追加（5日 > 25日）
        df['GC'] = df['株価移動平均線乖離率(5日)'] > df['株価移動平均線乖離率(25日)']

        # スクリーニング条件（より厳しく）
        filtered = df[
            (df['現在値'] <= max_price) &
            (df['RSI(%)'] < 50) &                            # RSI条件（より厳しく）
            (df['株価移動平均線乖離率(5日)'].abs() < 10) &
            (df['過去60日ボラティリティ(%)'] < 30) &      # ボラティリティ条件（より厳しく）
            (df['GC'] == True)                               # GCがTrueのみ
        ]

        print(f"▶ スクリーニング結果: {len(filtered)}件")

        results = []
        for _, row in filtered.iterrows():
            results.append({
                "code": str(row['コード']),
                "name": row['銘柄名'],
                "price": row['現在値'],
                "rsi": row['RSI(%)'],
                "volatility": row['過去60日ボラティリティ(%)'],
                "ma5_disparity": row['株価移動平均線乖離率(5日)'],
                "ma25_disparity": row['株価移動平均線乖離率(25日)'],
                "gc": row['GC']
            })

        return jsonify({"status": "ok", "results": results})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ローカルで実行
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)