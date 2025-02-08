import random
import time
from collections import defaultdict

# 初始化全局变量
p = [[[0, 0] for _ in range(5)] for __ in range(5)]  # 5x5x2结构，表示5个玩家每个有5张牌
a = [[0, 0] for _ in range(28)]
vis = [False] * 28
tot = 0
n = 5  # 假设有5个玩家

def my_shuffle():
    global p, a
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
    global n
    max_id = 0
    for i in range(1, n):
        if cmp(i, max_id, len_val):
            max_id = i
    return max_id
def psort(len_val):
    global n
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
def init():
    global tot, a
    random.seed(time.time())
    tot = 0
    # 初始化a数组（8-14每个数字4个花色）
    for i in range(8, 15):
        for j in range(1, 5):
            a[tot][0] = i
            a[tot][1] = j
            tot += 1
init()
my_shuffle()
las=psort(5)
for i in range(n):
    print(i,end=': ')
    for x in p[i]:
        print(x,end=' ')
    print()
for i in las:print(i,end=' ')
print()
