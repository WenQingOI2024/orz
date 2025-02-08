from flask import Flask, render_template, request, session, jsonify
from flask_socketio import SocketIO, join_room
import logging
import json
import random
from collections import defaultdict
import time


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRETKEY'
socketio = SocketIO()
socketio.init_app(app)
zaixian = []
money = {}
ready = {}
bet = {}
cheked = {}
ntcg = {}
user_id_dict = {}
GameStart = 0
steps = 0
jiangjingchi = 0
result = {}
sb = {}
# 封装原代码为函数


def poker_game(peoples):
    # 初始化全局变量
    p = [[[0, 0] for _ in range(5)] for __ in range(5)]  # 5x5x2结构，表示5个玩家每个有5张牌
    a = [[0, 0] for _ in range(28)]
    vis = [False] * 28
    tot = 0
    n = peoples  # 假设有5个玩家

    def my_shuffle():
        # global p, a
        indices = random.sample(range(28), 25)  # 生成25个不重复的随机索引
        idx = 0
        for i in range(5):
            for j in range(5):
                pos = indices[idx]
                p[i][j][0] = a[pos][0]
                p[i][j][1] = a[pos][1]
                idx += 1

    def dan(a_val, a_col, c_val, c_col):
        if a_val != c_val:
            return a_val > c_val
        else:
            return a_col > c_col

    def is_SC(id):
        suit = p[id][0][1]
        for i in range(1, 5):
            if p[id][i][1] != suit:
                return 0
        return suit

    def is_ST(id):
        pai = [card[0] for card in p[id]]
        pai.sort()
        for i in range(1, 5):
            if pai[i] != pai[i-1] + 1:
                return 0
        return pai[-1]

    def is_SF(id):
        return is_ST(id) != 0 and is_SC(id) != 0

    def is_BB(id):
        freq = [0] * 20
        for card in p[id]:
            freq[card[0]] += 1
        for i in range(8, 15):
            if freq[i] == 4:
                return i
        return 0

    def is_TA(id):
        freq = [0] * 20
        for card in p[id]:
            freq[card[0]] += 1
        for i in range(8, 15):
            if freq[i] == 3:
                return i
        return 0

    def is_PR(id):
        freq = [0] * 20
        for card in p[id]:
            freq[card[0]] += 1
        count = 0
        for i in range(8, 15):
            if freq[i] == 2:
                count += 1
        return count

    def is_CA(id):
        th = is_TA(id)
        se = is_PR(id)
        if th == 0 or se == 0 or se == 2:
            return 0
        return th

    def ask(id):
        if is_SF(id):
            return 8
        elif is_BB(id):
            return 7
        elif is_CA(id):
            return 6
        elif is_SC(id) != 0:
            return 5
        elif is_ST(id) != 0:
            return 4
        elif is_TA(id) != 0:
            return 3
        else:
            return is_PR(id)

    def MAX_val(id):
        max_val = p[id][0][0]
        max_col = p[id][0][1]
        for i in range(1, 5):
            current_val = p[id][i][0]
            current_col = p[id][i][1]
            if not dan(max_val, max_col, current_val, current_col):
                max_val, max_col = current_val, current_col
        return max_val

    def MAX_col(id):
        max_val = p[id][0][0]
        max_col = p[id][0][1]
        for i in range(1, 5):
            current_val = p[id][i][0]
            current_col = p[id][i][1]
            if not dan(max_val, max_col, current_val, current_col):
                max_val, max_col = current_val, current_col
        return max_col

    def cmp(i, j, len_val):
        if len_val == 5:
            a_rank = ask(i)
            b_rank = ask(j)
            if a_rank != b_rank:
                return a_rank > b_rank

            if a_rank in (8, 5, 4, 0):
                return dan(MAX_val(i), MAX_col(i), MAX_val(j), MAX_col(j))
            elif a_rank == 7:
                return is_BB(i) > is_BB(j)
            elif a_rank == 6:
                return is_CA(i) > is_CA(j)
            elif a_rank == 3:
                return is_TA(i) > is_TA(j)
            elif a_rank in (1, 2):
                t1 = defaultdict(int)
                t2 = defaultdict(int)
                for x in range(5):
                    t1[p[i][x][0]] += 1
                    t2[p[j][x][0]] += 1

                for x in range(14, 7, -1):
                    if t1[x] != t2[x] and (t1[x] == 2 or t2[x] == 2):
                        return t1[x] > t2[x]

                for x in range(14, 7, -1):
                    if t1[x] == 2:
                        c = max(card[1] for card in p[i] if card[0] == x)
                        d = max(card[1] for card in p[j] if card[0] == x)
                        return c > d
        else:
            a_val, a_col = p[i][1][0], p[i][1][1]
            for x in range(2, len_val + 1):
                current_val, current_col = p[i][x][0], p[i][x][1]
                if not dan(a_val, a_col, current_val, current_col):
                    a_val, a_col = current_val, current_col

            c_val, c_col = p[j][1][0], p[j][1][1]
            for x in range(2, len_val + 1):
                current_val, current_col = p[j][x][0], p[j][x][1]
                if not dan(c_val, c_col, current_val, current_col):
                    c_val, c_col = current_val, current_col

            return dan(a_val, a_col, c_val, c_col)
        return False

    def get_max_id(len_val):
        # global n
        max_id = 0
        for i in range(1, n):
            if cmp(i, max_id, len_val):
                max_id = i
        return max_id

    def psort(len_val):
        # global n
        rnk = [0]*5
        for i in range(0, n):
            rnk[i] = i
        for i in range(0, n):
            for j in range(1, n-i):
                if cmp(rnk[j], rnk[j-1], len_val):
                    nw = rnk[j-1]
                    rnk[j-1] = rnk[j]
                    rnk[j] = nw
        return rnk

    def INIT():
        # global tot, a
        random.seed(time.time())
        tot = 0
        # 初始化a数组（8-14每个数字4个花色）
        for i in range(8, 15):
            for j in range(1, 5):
                a[tot][0] = i
                a[tot][1] = j
                tot += 1

    INIT()
    # 洗牌
    my_shuffle()
    # 获取最大手牌的索引
    max_id = get_max_id(5)

    return {
        "hands": p,
        "max1": get_max_id(1),
        "max2": get_max_id(2),
        "max3": get_max_id(3),
        "max_id": max_id
    }


@app.route('/')
def root():
    ip = request.remote_addr
    logging.debug(ip)
    username = ip   # 这里是用户名设定
    session['username'] = username   # 这里用的session进行操作
    return render_template('index.html', ip=ip)


@app.route('/playid/')
def plid():
    return json.dumps(user_id_dict, sort_keys=True, ensure_ascii=False)


@app.route('/postbet', methods=["POST"])
def gtbet():
    global bet
    betd = request.form.get("bet")
    betd = (int)(betd)
    print(betd)
    ip = request.remote_addr
    logging.debug(ip)
    bet.update({ip: betd})
    return str(0)


@app.route('/postck', methods=["POST"])
def gtck():
    global cheked
    ck = request.form.get("cheked")
    ck = (int)(ck)
    print(ck)
    if GameStart == 1:
        ip = request.remote_addr
        logging.debug(ip)
        cheked.update({ip: ck})
    return str(0)


@app.route('/red')
def jianjian():
    global ntcg
    ip = request.remote_addr
    logging.debug(ip)
    ntcg.update({ip: 0})
    return str(0)


@app.route('/checked/')
def checked():
    return json.dumps(cheked, sort_keys=True, ensure_ascii=False)


@app.route('/bets/')
def bets():
    return json.dumps(bet, sort_keys=True, ensure_ascii=False)


@app.route('/people/')
def people():
    return json.dumps(zaixian)


@app.route('/play_poker/', methods=['GET'])
def play_poker():
    return jsonify(result)


@app.route('/money/')
def MON():
    # print(money)
    return json.dumps(money, sort_keys=True, ensure_ascii=False)


@app.route('/gameid/')
def GMId():
    return json.dumps(user_id_dict, sort_keys=True, ensure_ascii=False)


@app.route('/steps/')
def stps():
    return str(steps)


@app.route('/ntcg/')
def niyaogai():
    return json.dumps(ntcg, sort_keys=True, ensure_ascii=False)


@app.route('/gethands/<n>')
def hds(n):
    ip = request.remote_addr
    logging.debug(ip)
    global steps
    if steps >= int(n):
        print(result['hands'])
        return json.dumps(result['hands'][int(n)][int(user_id_dict[ip])-1])
    else:
        return str(0)


@app.route('/gamesta/')
def gamesta():
    global GameStart
    global user_id_dict
    global result
    global steps
    global cheked
    global bet
    global ntcg
    if GameStart == 0:
        flag = 1
        # print("len "+str(len(zaixian)))
        for u in zaixian:
            print(u+" "+ready[u])
            if ready[u] == "NO":
                flag = 0
        if len(zaixian) == 0:
            flag = 0
        GameStart = flag
        if flag == 1:  # start
            steps = 1
            print(zaixian)
            user_id_dict = {ip: index + 1 for index, ip in enumerate(zaixian)}
            print(user_id_dict)
            result = poker_game(len(zaixian))
    else:  # GAMEmain
        print("===start===")
        flag = 1
        for u in zaixian:
            if cheked[u] == 0:
                flag = 0
        if flag == 1:  # 都下注完了
            # 要改的
            maxn = 0
            for u in zaixian:
                maxn = max(maxn, bet[u])
            for u in zaixian:
                if bet[u] != maxn:
                    ntcg[u] = maxn
                    ntcg.update({u: maxn-bet[u]})
            # 下一轮了
            for u in zaixian:
                cheked[u] = 0
                bet[u] = 0
            steps = steps+1
            if steps==4:#结束了
                # 清空：
                GameStart=0
                steps=0
                for u in zaixian:
                    ready[u] = "NO"
                    cheked[u] = 0
                    result=sb

    return str(GameStart)


@app.route('/rea/')
def rea():
    return json.dumps(ready, sort_keys=True, ensure_ascii=False)


@app.route('/ChangeReady/')
def ChangeReady():
    ip = request.remote_addr
    logging.debug(ip)
    # print(ip)
    if GameStart == 0:
        if ready[ip] == "NO":
            ready[ip] = "YES"
        else:
            ready[ip] = "NO"
    return json.dumps(ready, sort_keys=True, ensure_ascii=False)


@socketio.on('connect')
def connected_msg():
    print('用户已连接！')
    print("Session:" + session.get('username'))
    if session.get('username') in money.keys():
        print("###> OLD money")
    else:
        print("###> NEW money")
        money.update({session.get('username'): 10000})

    if session.get('username') in ready.keys():
        print("###> OLD ready")
    else:
        print("###> NEW ready")
        if GameStart == 1:
            print("This user cannot play this game.")
            ready.update({session.get('username'): "游戏已经开始了！等待游戏结束并刷新!"})
            zaixian.remove(session.get('username'))
        else:
            ready.update({session.get('username'): "NO"})

    if session.get('username') in cheked.keys():
        print("###asd> OLD cheked---")
    else:
        print("###asd> NEW cheked---")
        cheked.update({session.get('username'): 0})

    if session.get('username') in ntcg.keys():
        print("###asd> OLD ntcg---")
    else:
        print("###asd> NEW ntcg---")
        ntcg.update({session.get('username'): 0})

    zaixian.append(session.get('username'))
    for i in zaixian:
        print(i)


@socketio.on('disconnect')
def disconnect_msg():
    print('用户断开连接！')
    print("Session:" + session.get('username'))
    zaixian.remove(session.get('username'))
    for i in zaixian:
        print(i)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
