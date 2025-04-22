from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/screen', methods=['GET'])
def screen():
    try:
        # クエリパラメータで価格上限を取得（デフォルト: 2000円）
        max_price = float(request.args.get('price', 2000))

        # CSVファイル読み込み（同じフォルダ内）
        df = pd.read_csv('priced_data.csv', encoding='utf-8')

        # 欠損値のある行を除外
        df = df.dropna(subset=[
            '現在値', 'RSI(%)', '過去60日ボラティリティ(%)',
            '株価移動平均線(5日)', '株価移動平均線(25日)'
        ])

        # 型変換
        df['現在値'] = pd.to_numeric(df['現在値'], errors='coerce')
        df['RSI(%)'] = pd.to_numeric(df['RSI(%)'], errors='coerce')
        df['過去60日ボラティリティ(%)'] = pd.to_numeric(df['過去60日ボラティリティ(%)'], errors='coerce')
        df['株価移動平均線(5日)'] = pd.to_numeric(df['株価移動平均線(5日)'], errors='coerce')
        df['株価移動平均線(25日)'] = pd.to_numeric(df['株価移動平均線(25日)'], errors='coerce')

        # ゴールデンクロス判定
        df['GC'] = df['株価移動平均線(5日)'] > df['株価移動平均線(25日)']

        # フィルタ条件
        filtered = df[
            (df['現在値'] <= max_price) &
            (df['RSI(%)'] >= 40) & (df['RSI(%)'] <= 60) &
            (df['過去60日ボラティリティ(%)'] <= 5) &
            (df['GC'] == True)
        ]

        # 必要な列だけ抽出して JSON 形式で返す
        result = filtered[['コード', '銘柄名', '現在値', 'RSI(%)', '過去60日ボラティリティ(%)', 'GC']].head(20)

        return jsonify({
            "status": "ok",
            "count": len(result),
            "results": result.to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)