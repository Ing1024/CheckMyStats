from flask import Flask, render_template
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

app = Flask(__name__)

# 读取数据
df = pd.read_csv('data/lebron_james_game_stats.csv')

# 数据预处理（已包含年份的日期处理）
df['日期'] = pd.to_datetime(df['日期'])  # 直接解析完整日期格式（YYYY-MM-DD）
df_sorted = df.sort_values(by='日期', ascending=True)  # 按时间升序排列

# 生成当日数据横向柱状图
def create_today_stats_bar_chart():
    latest_game = df_sorted.iloc[-1]  # 获取最新一场比赛
    categories = ['得分', '篮板', '助攻', '失误', '抢断', '盖帽']
    values = [latest_game[cat] for cat in categories]

    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker=dict(
            color=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4'],
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        )
    ))

    fig.update_layout(
        title=f"当日比赛数据 ({latest_game['日期'].strftime('%Y-%m-%d')} vs {latest_game['对手']})",
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_visible=False,
        margin=dict(l=120, r=20, t=50, b=20)
    )
    return fig.to_html(full_html=False)

# 生成整个赛季得分变化趋势折线图
def create_season_score_line_chart():
    fig = px.line(
        df_sorted,  # 使用按日期排序后的数据
        x='日期',
        y='得分',
        title='整个赛季得分变化趋势',
        markers=True,
        labels={'日期': '日期', '得分': '得分'}  # 自定义坐标轴标签
    )

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=40, r=20, t=50, b=20),
        xaxis=dict(
            tickformat='%Y-%m-%d',  # 显示完整日期格式
            tickangle=45  # 旋转x轴标签
        )
    )
    return fig.to_html(full_html=False)

@app.route('/')
def index():
    latest_game = df_sorted.iloc[-1]
    return render_template('index.html',
                           bar_chart=create_today_stats_bar_chart(),
                           line_chart=create_season_score_line_chart(),
                           last_game_date=latest_game['日期'].strftime('%Y-%m-%d'),
                           last_game_opponent=latest_game['对手'])

if __name__ == '__main__':
    app.run(debug=True)