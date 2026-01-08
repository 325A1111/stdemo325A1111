import streamlit as st
import random
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import MaxNLocator

#チンチロゲームクラス
class chinchiro:
    #メンバ変数
    def __init__(self):
        self.player = player()
        self.enemy = player()
        self.money = 10000
        self.bet = 0
        self.bet_flg = False    #賭け金を未確定ならFalse
        self.cnt = 0            #サイコロを振った回数
        self.money_history = [10000]    #ラウンド毎の所持金の推移に使用
        self.result = None      #引き分け　勝利　敗北　の３種
        self.win_streak = 0 #連勝数
        self.judge_flg = False
        
    #賭け金
    def betting(self):
        if not self.bet_flg:
            st.write(f"所持金 : {self.money}")
            self.bet = st.number_input("賭け金を入力",
                                       max_value=self.money)   #上限は所持金まで  
            if st.button("賭け金を確定"):
                self.bet_flg = True     
                self.money -= self.bet
        else:
            st.write(f"賭け金はすでに入力済みです {self.bet}")
    
    #役判定 [役名,役の強さ,倍率]　
    def comb(self,nums):
        if nums[0] == nums[1] == nums[2]: #ゾロ目
            if nums[0] == 1:
                return ["ピンゾロ",13,6]
            else:
                return [f"ゾロ目 : {nums[0]}",nums[0]+6,4]
        elif nums == [4,5,6]:
            return ["シゴロ",7,3]
        elif nums == [1,2,3]:#一二三
            return ["ヒフミ",-1,None]
        elif nums[0] == nums[1] !=nums[2]:
            return [f"目あり : {nums[2]}",nums[2],2]
        elif nums[0] != nums[1] ==nums[2]:
            return [f"目あり : {nums[0]}",nums[0],2]
        else:
            return ["役無し",0,None]
    
    #ターン　ダイスを振る
    def turn(self,contender,flg):
        dice = [random.randint(1,6) for i in range(3)]
        comb = game.comb(sorted(dice))   #役を判定するためソートして渡す
        contender.update_max(comb)
        
        if flg == 0:
            st.write(f"あなたの最大の役 : {contender.max_comb[0]}")
        else:
            st.write(f"敵の最大の役 : {contender.max_comb[0]}")      
        st.write(dice)
        
    #勝敗判定
    def judge(self):
        if self.player.max_comb[1] == self.enemy.max_comb[1]:
            self.result = "引き分け"
        elif self.player.max_comb[1] > self.enemy.max_comb[1]:
            self.win_streak +=1
            self.result = "勝利"      
        else:
            self.win_streak = 0
            self.result = "敗北"
            
    #結果表示        
    def show_result(self):
        st.title(self.result)
        match self.result:
            case "引き分け":
                st.write(f"役  {self.player.max_comb[0]} / {self.enemy.max_comb[0]}")
                self.money+=self.bet
                st.write(f"賭け金 {self.bet} が返還されました")
                
            case "勝利":
                st.write(f"賭け金       {self.bet}")
                st.write(f"倍率    {self.player.max_comb[0]} , {self.player.max_comb[2]}")
                income = self.bet*self.player.max_comb[2]*self.win_streak
                if self.win_streak >=2:
                    st.write(f"連勝ボーナス     {self.win_streak}")
                st.write(f"計   {income}")
                self.money+=income
            case "敗北":
                st.write(f"役  {self.player.max_comb[0]} / {self.enemy.max_comb[0]}")
                if self.player.max_comb[1] == -1:
                    self.money = self.money-self.bet
                    st.write("ヒフミにより賭け金の倍失いました")  
                  
                
    #所持金の推移グラフ      
    def show_money_graph(self):
        rcParams['font.family'] = 'MS Gothic'   #日本語に
        rounds = list(range(0, len(self.money_history)))    #x軸に使用　0から所持金の推移リストの要素数まで
        
        fig,ax = plt.subplots()
        ax.plot(rounds,self.money_history,marker = "o")
        ax.set_xlabel("ラウンド")
        ax.set_ylabel("所持金")
        ax.set_title("所持金の推移")
        ax.grid(True)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True)) #グラフの目盛りを整数にする

        st.pyplot(fig)
    
    #次ラウンドのため　勝負に関わる部分のリセット
    def next_round_set(self):
        self.cnt = 0
        self.bet_flg = False
        self.judge_flg = False
        self.player.__init__()
        self.enemy.__init__()
        
#プレイヤークラス
class player:
    #メンバ変数
    def __init__(self):
        self.max_comb = [None,-2,None]  #最弱のヒフミの強さは-1
        
    def update_max(self,comb):
        if comb[1] > self.max_comb[1]:
            self.max_comb = comb

#メイン
st.image("saikoro.png")
st.title("チンチロ")

#ゲームを生成　セッションに保存
if "game" not in st.session_state:
    st.session_state.game = chinchiro()
game = st.session_state.game

#最初はロールフェーズから
if "phase" not in st.session_state:
    st.session_state.phase = "roll"
 
col1,col2 = st.columns(2)
 
match st.session_state.phase:#switch文みたいな
    case "roll":#ロールフェーズ              
        game.betting()
        if st.button(f"サイコロを振る",
                    disabled = (game.bet_flg == False) or game.cnt >=4):#賭け金が未確定or5回振ったら押せない
            with col1:
                game.turn(game.player,0)            
            with col2:
                game.turn(game.enemy,1)
            game.cnt+=1
            if game.cnt >= 5:
                st.button("結果を見る")
                st.session_state.phase = "judge"    #judgeフェーズに切り替え
            else:
                st.write(f"あと{5-game.cnt}回")

    case "judge":#ジャッジフェーズ 
        #streamlitの再実行対策  
        if game.judge_flg == False: 
            game.judge()
            game.show_result()
            game.judge_flg = True
            
        game.money_history.append(game.money)
        st.write(f"所持金 : {game.money}")
        game.show_money_graph()
        st.session_state.phase = "roll" #ロールフェーズに切り替え
        game.next_round_set()
        st.button("次の勝負") #ボタンは飾りだがうまくいく