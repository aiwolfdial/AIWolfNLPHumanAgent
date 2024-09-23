import math
import time
import curses
from typing import Callable
from AIWolfNLAgentPython.player.agent import Agent
from timeout_decorator import timeout, TimeoutError

class Human(Agent):

    def initialize(self, name:str) -> None:
        self.time_limit:float = 1.0
        self.received:list = []
        self.gameContinue:bool = True

        self.name:str = name
    
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
        curses.curs_set(1)  # カーソルを表示
        stdscr.timeout(1000) # getchの上限を設定

        input_text = []

        while True:
            current_time = time.time()
            elapsed_time = (int)(current_time - start_time)
            remain_time = self.time_limit - elapsed_time

            stdscr.addstr(0, 0, "Time:" + str(remain_time))
            stdscr.move(1, len(input_text))  # カーソルの位置を調整

            key = stdscr.getch()  # 1文字ずつキーを取得
            
            if key == -1:
                continue

            if key == 10:  # Enterキー (ASCIIコード10)
                break
            elif key in (127, 8, curses.KEY_BACKSPACE):  # バックスペースキーの様々な可能性を考慮
                if input_text:
                    input_text.pop()
                    stdscr.move(1, 0)
                    stdscr.clrtoeol()  # 1行目の入力部分をクリア
                    stdscr.addstr(1, 0, ''.join(input_text))  # 入力を再描画
                    stdscr.move(1, len(input_text))  # カーソルの位置を調整
            else:
                input_text.append(chr(key))  # 入力されたキーを追加
                stdscr.addstr(1, 0, ''.join(input_text))  # 入力を再描画

            stdscr.refresh()
        
        return ''.join(input_text)

    def set_received(self, received: list) -> None:
        return super().set_received(received)
    
    def parse_info(self, receive: str) -> None:
        return super().parse_info(receive)
    
    def get_info(self) -> None:
        return super().get_info()
    
    def initialize() -> None:
        return super().initialize()
    
    def daily_initialize(self) -> None:
        return super().daily_initialize()
    
    def daily_finish(self) -> None:
        return super().daily_finish()
    
    def get_name(self) -> str:
        return super().get_name()
    
    def get_role(self) -> str:
        return super().get_role()
    
    def talk(self) -> str:
        user_input = curses.wrapper(self.input_with_timelimit)

        return super().talk()
    
    def vote(self) -> int:
        return super().vote()
    
    def whisper(self) -> None:
        return super().whisper()
    
    def finish(self) -> str:
        self.gameContinue = False
    
    def action(self) -> str:
        return super().action()
    
    def hand_over(self, new_agent) -> None:
        return super().hand_over(new_agent)