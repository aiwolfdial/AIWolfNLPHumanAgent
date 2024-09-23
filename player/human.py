import configparser
import math
import json
import curses
import time
from timeout_decorator import timeout, TimeoutError
from typing import Callable
from aiwolf_nlp_common import util
from aiwolf_nlp_common import AIWolfNLPAction

class Human:
    def __init__(self, inifile:configparser.ConfigParser, name:str, is_hand_over:bool=False):
       self.time_limit:float = 1.0
       self.name:str = name
       self.received:list = []
       self.gameContinue:bool = True

       random_talk_path:str = inifile.get("filePath","random_talk")
       _ = util.check_config(random_talk_path)
       
       self.comments:list = util.read_text(random_talk_path)

    def with_timelimit(func:Callable):

        def _wrapper(self, *args, **keywords):
            time_limit:float = 0.0
            result:str = ""

            # set time limit
            if math.isclose(self.time_limit, 0, abs_tol=1e-10)  and keywords.get("time_limit") is None:
                raise ValueError(func.__name__ + ": time limit is not found")
            elif math.isclose(self.time_limit, 0, abs_tol=1e-10):
                time_limit = keywords.get("time_limit")
            elif keywords.get("time_limit") is None:
                time_limit = self.time_limit
            else:
                time_limit = min(self.time_limit, keywords.get("time_limit"))

            # define local function
            @timeout(time_limit)
            def execute_func(self, *args, **keywords):
                # execute function
                if len(keywords) == 0:
                    result = func(self)
                else:
                    result = func(self, *args, **keywords)

                return result
            
            try:
                # call local function
                result = execute_func(self, *args, **keywords)
            except TimeoutError:
                print(func.__name__ + " has run out of time.")

            return result

        return _wrapper
    
    def input_with_timelimit(self, stdscr:curses.window) -> str:
        start_time = time.time()
        max_y, max_x = stdscr.getmaxyx()

        # 描画箇所
        y_pos = 0
        x_pos = 0

        # 前の表示を削除
        stdscr.clear()
        stdscr.refresh()

        stdscr.addstr(0, 0, "Remain Time:" + str(1000))
        y_pos += 1

        stdscr.addstr(y_pos, 0, "You are " + self.gameInfo["agent"] + ".")
        y_pos += 1

        stdscr.addstr(y_pos, 0, "Your role is " + self.role + ".")
        y_pos += 1


        # 見えやすくするために1行開ける
        y_pos += 1

        y_pos = self.output_talk_history(stdscr=stdscr, y_pos=y_pos)
        is_back = is_input = False
        is_y_decrement = False

        # 見えやすくするために1行開ける
        y_pos += 1

        input_start_pos = y_pos
        input_prompt = "input message >>:"

        stdscr.addstr(input_start_pos, 0, input_prompt)
        x_pos = len(input_prompt)

        curses.curs_set(1)  # カーソルを表示
        stdscr.timeout(1000) # getchの上限を設定

        input_text = []

        while True:
            current_time = time.time()
            elapsed_time = (int)(current_time - start_time)
            remain_time = self.time_limit - elapsed_time

            stdscr.addstr(0, 0, "Remain Time:" + str(remain_time))
            stdscr.addstr(input_start_pos, 0, input_prompt)

            if is_y_decrement:
                stdscr.move(y_pos, max_x - 1)  # カーソルの位置を調整
            else:
                stdscr.move(y_pos, x_pos)  # カーソルの位置を調整
            
            is_back = is_input = False
            is_y_decrement = False

            key = stdscr.getch()  # 1文字ずつキーを取得
            
            if key == -1:
                continue

            if key == 10 and len(input_text) == 0:
                continue

            if key == 10:  # Enterキー (ASCIIコード10)
                break
            elif key in (127, 8, curses.KEY_BACKSPACE):  # バックスペースキーの様々な可能性を考慮
                if input_text:
                    input_text.pop()
                    is_back = True
                    # stdscr.move(y_pos, 0)
                    # stdscr.clrtoeol()  # 1行目の入力部分をクリア
                    # stdscr.addstr(y_pos, 0, ''.join(input_text))  # 入力を再描画
                    # stdscr.move(y_pos, len(input_text))  # カーソルの位置を調整
            else:
                input_text.append(chr(key))  # 入力されたキーを追加      
                is_input = True

            write_start_pos = 0
            write_y_pos = input_start_pos
            one_line_chars = max_x - len(input_prompt)
            remain_text = len(input_text)
            write_text = []

            while remain_text > 0:
                write_end_pos = write_start_pos + one_line_chars
                write_text = input_text[write_start_pos:write_end_pos]
                stdscr.move(write_y_pos, 0)  # カーソルの位置を調整
                stdscr.clrtoeol()  # カーソルがある部分の入力部分をクリア
                stdscr.move(write_y_pos+1, 0)  # カーソルの位置を調整
                stdscr.clrtoeol()  # カーソルがある部分の入力部分をクリア
                stdscr.addstr(write_y_pos, len(input_prompt), ''.join(write_text))  # 入力を再描画

                remain_text -= len(write_text)
                write_start_pos = write_end_pos
                write_y_pos += 1
            
            if len(write_text)  == one_line_chars - 1 and is_back:
                y_pos -= 1
                is_y_decrement = True
            elif len(write_text) == one_line_chars:
                x_pos = len(input_prompt)

                if is_input:
                    y_pos += 1
            else:
                x_pos = len(input_prompt) + len(write_text)
            
            if len(write_text) == 0:
                stdscr.move(input_start_pos, 0)  # カーソルの位置を調整
                stdscr.clrtoeol()  # カーソルがある部分の入力部分をクリア

            stdscr.refresh()
        
        return ''.join(input_text)
    
    def output_talk_history(self, stdscr:curses.window, y_pos:int) -> int:
        max_y, max_x = stdscr.getmaxyx()

        # 見えやすくするための改行　
        y_pos += 1

        stdscr.addstr(y_pos, 0, "====== Talk History =====")
        y_pos += 1

        for talk in self.talkHistory:
            talk_player = talk["agent"]
            talk_content = talk["text"]
            talk_display = talk_player + " : " + talk_content

            stdscr.addstr(y_pos, 0, talk_display)

            y_pos += len(talk_display)//max_y + 1
        
        return y_pos
    
    def send_agent_index(func:Callable):
        
        def _wrapper(self,*args, **keywords):
            
            # execute function
            if len(keywords) == 0:
                result:int = func(self)
            else:
                result:int = func(self, *args, **keywords)

            if type(result) is not int:
                raise ValueError("Functions with the send_agent_index decorator must return an int type")
            
            return util.index_to_agent_format(agent_index=result)
        
        return _wrapper

    def set_received(self, received:list) -> None:
        self.received = received

    def parse_info(self, receive: str) -> None:

        received_list = receive.split("}\n{")

        for index in range(len(received_list)):
            received_list[index] = received_list[index].rstrip()

            count = util.check_json_missing_part(responces=received_list[index])

            while count < 0:
                received_list[index] = "{" + received_list[index]
                count += 1
            
            while count > 0:
                received_list[index] += "}"
                count -= 1
            
            if received_list[index][0] != "{":
                received_list[index] = "{" + received_list[index] + "}"

            self.received.append(received_list[index])
    
    def get_info(self):
        try:
            test = self.received.pop(0)
            data = json.loads(test)
        except:
            print(test)
            data = json.loads(test)

        if data.get("gameInfo") is not None:
            self.gameInfo = data["gameInfo"]
        
        if data.get("gameSetting") is not None:
            self.gameSetting = data["gameSetting"]

        if data.get("talkHistory") is not None:
            self.talkHistory = data["talkHistory"]
        
        if data.get("whisperHistory") is not None:
            self.whisperHistory = data["whisperHistory"]

        self.request = data["request"]
   
    def initialize(self) -> None:
        self.index:int = util.get_index_from_name(agent_name=self.gameInfo["agent"])

        self.time_limit:float = int(self.gameSetting["actionTimeout"])/1000 # ms -> s
        self.role:str = self.gameInfo["roleMap"][self.gameInfo["agent"]]

        print("You are " + self.gameInfo["agent"] + ".")
        print("Your role is " + self.role + ".")

    def daily_initialize(self) -> None:
        self.alive = []

        for agent_name in self.gameInfo["statusMap"]:
            agent_num:int = util.get_index_from_name(agent_name=agent_name)

            if self.gameInfo["statusMap"][agent_name] == "ALIVE" and agent_num != self.index:
                self.alive.append(agent_num)

    def daily_finish(self) -> None:
        pass
    
    @with_timelimit
    def get_name(self) -> str:
        return self.name
    
    @with_timelimit
    def get_role(self) -> str:
        return self.role
    
    @with_timelimit
    def talk(self) -> str:
        comment:str = curses.wrapper(self.input_with_timelimit)

        for talk in self.talkHistory:
            talk_player = talk["agent"]
            talk_content = talk["text"]
            talk_display = talk_player + " : " + talk_content
            print(talk_display)

        return comment
    
    @with_timelimit
    @send_agent_index
    def vote(self) -> int:
        vote_target:int = util.random_select(self.alive)
        return vote_target
    
    @with_timelimit
    def whisper(self) -> None:
        pass

    def finish(self) -> str:
        self.gameContinue = False

    def action(self) -> str:

        if AIWolfNLPAction.is_initialize(request=self.request):
            self.initialize()
        elif AIWolfNLPAction.is_name(request=self.request):
            return self.get_name()
        elif AIWolfNLPAction.is_role(request=self.request):
            return self.get_role()
        elif AIWolfNLPAction.is_daily_initialize(request=self.request):
            self.daily_initialize()
        elif AIWolfNLPAction.is_daily_finish(request=self.request):
            self.daily_finish()
        elif AIWolfNLPAction.is_talk(request=self.request):
            return self.talk()
        elif AIWolfNLPAction.is_vote(request=self.request):
            return self.vote()
        elif AIWolfNLPAction.is_whisper(request=self.request):
            self.whisper()
        elif AIWolfNLPAction.is_finish(request=self.request):
            self.finish()
        
        return ""
    
    def hand_over(self, new_agent) -> None:
        # __init__
        new_agent.name = self.name
        new_agent.received = self.received
        new_agent.gameContinue = self.gameContinue
        new_agent.comments = self.comments
        new_agent.received = self.received

        # get_info
        if hasattr(self,'gameInfo'):
            new_agent.gameInfo = self.gameInfo
        
        if hasattr(self,'gameSetting'):
            new_agent.gameSetting = self.gameSetting

        if hasattr(self,'talkHistory'):
            new_agent.talkHistory = self.talkHistory
        
        if hasattr(self,'whisperHistory'):
            new_agent.whisperHistory = self.whisperHistory

        new_agent.request = self.request

        # initialize
        new_agent.index = self.index
        new_agent.role = self.role
        new_agent.time_limit = self.time_limit