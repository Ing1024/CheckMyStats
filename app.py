from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from data_catch import data_catch

app = Flask(__name__)

data = [('https://nba.hupu.com/players/lebronjames-650.html','data/lebron_james_game_stats.csv'),
        ('https://nba.hupu.com/players/victorwembanyama-152987.html', 'data/victor_wembanyama_game_stats.csv'),
        ('https://nba.hupu.com/players/lukadoncic-150648.html', 'data/luka_doncic_game_stats.csv'),
        ('https://nba.hupu.com/players/stephencurry-3311.html', 'data/stephen_curry_game_stats.csv'),
        ('https://nba.hupu.com/players/jimmybutler-3583.html', 'data/jimmy_butler_game_stats.csv'),
        ('https://nba.hupu.com/players/shaigilgeousalexander-150959.html', 'data/shaigilgeousalexander_game_stats.csv'),
        ('https://nba.hupu.com/players/nikolajokic-4943.html', 'data/nikolajokic_game_stats.csv'),
        ('https://nba.hupu.com/players/joelembiid-4958.html', 'data/joel_embiid_game_stats.csv'),
        ('https://nba.hupu.com/players/bensimmons-150163.html','data/ben_simmons_game_stats.csv')
        ]

# 球员信息
players = {
    'lebron_james': {'name': '勒布朗·詹姆斯', 'file': 'data/lebron_james_game_stats.csv'},
    'victor_wembanyama': {'name': '维克托·文班亚马', 'file': 'data/victor_wembanyama_game_stats.csv'},
    'luka_doncic': {'name': '卢卡·东契奇', 'file': 'data/luka_doncic_game_stats.csv'},
    'stephen_curry': {'name': '斯蒂芬·库里', 'file': 'data/stephen_curry_game_stats.csv'},
    'jimmy_butler': {'name': '吉米·巴特勒', 'file': 'data/jimmy_butler_game_stats.csv'},
    'shaigilgeousalexander': {'name': '谢伊·吉尔杰斯·亚历山大', 'file': 'data/shaigilgeousalexander_game_stats.csv'},
    'nikolajokic': {'name': '尼古拉·约基奇', 'file': 'data/nikolajokic_game_stats.csv'},
    'joel_embiid': {'name': '乔尔·恩比德', 'file': 'data/joel_embiid_game_stats.csv'},
    'ben_simmons': {'name': '本·西蒙斯', 'file': 'data/ben_simmons_game_stats.csv'}
}

def update_data():
    """更新数据"""
    print("正在更新数据...")
    for i in range(len(data)):
        data_catch(data[i][0],data[i][1])
    print("数据更新完成！")

# 读取数据
def load_data(player_id):
    """加载数据"""
    df = pd.read_csv(players[player_id]['file'])
    df['日期'] = pd.to_datetime(df['日期'])  # 解析日期
    return df.sort_values(by='日期', ascending=False)  # 按时间降序排列

# 生成比赛数据横向柱状图
def create_game_stats_bar_chart(game_data):
    categories = ['盖帽','抢断', '失误', '助攻', '篮板', '得分']
    values = [game_data[cat] for cat in categories]

    fig = go.Figure(go.Bar(
        y=categories,
        x=values,
        orientation='h',
        marker=dict(
            color=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4'],
            line=dict(color='rgba(255,255,255,0.3)', width=1)
        ),
        text=values,  # 添加数据标签
        textposition='outside'  # 将标签放在条形图外部
    ))

    # 设置x轴范围
    fig.update_xaxes(range=[0, 50])  # 设置所有数据的上限为50

    fig.update_layout(
        title=f"比赛数据 ({game_data['日期'].strftime('%Y-%m-%d')} vs {game_data['对手']})",
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_visible=False,
        margin=dict(l=120, r=20, t=50, b=20),
        showlegend=False  # 隐藏图例
    )
    return fig.to_json()

# 生成整个赛季得分变化趋势折线图
def create_season_score_line_chart(df_sorted):
    fig = px.line(
        df_sorted.sort_values(by='日期', ascending=True),  # 按时间升序排列
        x='日期',
        y='得分',
        title='整个赛季得分变化趋势',
        markers=True,
        labels={'日期': '日期', '得分': '得分'}
    )

    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        margin=dict(l=40, r=20, t=50, b=20),
        xaxis=dict(
            tickformat='%Y-%m-%d',
            tickangle=45
        ),
        yaxis=dict(
            range=[0, 60]  # 设置纵轴区间为[0, 60]
        ),
        width=1200,  # 让图表宽度自适应容器
        height=400,  # 设置固定高度
        autosize=True  # 启用自动调整大小
    )
    return fig.to_html(full_html=False)

@app.route('/')
def index():
    return render_template('index.html', players=players)

@app.route('/player/<player_id>')
def player_stats(player_id):
    if player_id not in players:
        return "球员不存在", 404
        
    df_sorted = load_data(player_id)
    
    # 获取所有比赛日期和对手信息
    games = df_sorted[['日期', '对手']].apply(
        lambda x: {'date': x['日期'].strftime('%Y-%m-%d'), 'opponent': x['对手']}, 
        axis=1
    ).tolist()
    
    latest_game = df_sorted.iloc[0]  # 获取最新一场比赛
    return render_template('player_stats.html',
                           player_name=players[player_id]['name'],
                           bar_chart=create_game_stats_bar_chart(latest_game),
                           line_chart=create_season_score_line_chart(df_sorted),
                           games=games,
                           last_game_date=latest_game['日期'].strftime('%Y-%m-%d'),
                           last_game_opponent=latest_game['对手'])

@app.route('/get_game_stats/<player_id>')
def get_game_stats(player_id):
    date = request.args.get('date')
    df_sorted = load_data(player_id)
    # 确保日期格式一致
    game_data = df_sorted[df_sorted['日期'].dt.strftime('%Y-%m-%d') == date].iloc[0]
    return jsonify({
        'chart': create_game_stats_bar_chart(game_data)
    })

@app.route('/get_season_trend/<player_id>')
def get_season_trend(player_id):
    df_sorted = load_data(player_id)
    return jsonify({
        'chart': create_season_score_line_chart(df_sorted)
    })

if __name__ == '__main__':
    # 启动服务器前更新数据
    update_data()
    # 启动服务器
    app.run(debug=True)