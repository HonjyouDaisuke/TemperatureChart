import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# PHP API のURL（実際のサーバーに合わせて変更）
API_URL = "https://hisseki-misaki.sakura.ne.jp/raspberrypi/get_sensor_data.php"

def fetch_data(start_date: str, end_date: str) -> pd.DataFrame:
    params = {
        "start": start_date,
        "end": end_date
    }
    st.text(params)
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return pd.DataFrame(response.json())

# Streamlit アプリ
st.title("温度・湿度グラフ")

# デフォルトで直近1週間
default_end = datetime.today()
default_start = default_end - timedelta(days=7)

start = st.date_input("開始日", default_start)
end = st.date_input("終了日", default_end)

# 日付が有効な範囲であれば取得
if start > end:
    st.error("開始日は終了日より前にしてください。")
else:
    try:
        df = fetch_data(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        if df.empty:
            st.warning("データが見つかりませんでした。")
        else:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # 移動平均（例：5点）
            df['temp_ma'] = df['temperature'].rolling(window=31).mean()
            df['hum_ma'] = df['humidity'].rolling(window=31).mean()

            fig = go.Figure()

            # 温度
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['temperature'],
                name='温度 (°C)', yaxis='y1', mode='lines', line=dict(color='red')
            ))
            # 温度移動平均
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['temp_ma'],
                name='温度移動平均', yaxis='y1', mode='lines', line=dict(color='orange', dash='dash')
            ))

            # 湿度
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['humidity'],
                name='湿度 (%)', yaxis='y2', mode='lines', line=dict(color='blue')
            ))
            # 湿度移動平均
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df['hum_ma'],
                name='湿度移動平均', yaxis='y2', mode='lines', line=dict(color='skyblue', dash='dash')
            ))

            fig.update_layout(
                xaxis=dict(title='日時'),
                yaxis=dict(title='温度 (°C)', side='left'),
                yaxis2=dict(title='湿度 (%)', overlaying='y', side='right'),
                legend=dict(x=0, y=1),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"データ取得エラー: {e}")
