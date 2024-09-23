import configparser
from aiwolf_nlp_common.connection import(
    SSHServer
)
from player.human import Human
from aiwolf_nlp_common import util

def main(sock: SSHServer, inifile:configparser.ConfigParser, received:list, name:str):
    agent = Human(inifile=inifile, name=name)

    if received != None: agent.set_received(received=received)

    while agent.gameContinue:

        if len(agent.received) == 0:
            agent.parse_info(receive=sock.receive())
        
        agent.get_info()
        message = agent.action()

        if message != "":
            sock.send(message=message)

    return agent.received if len(agent.received) != 0 else None

if __name__ == "__main__":
    config_path = "./res/config.ini"

    inifile = util.check_config(config_path=config_path)
    inifile.read(config_path,"UTF-8")

    while True:

        sock = SSHServer(inifile=inifile, name=inifile.get("agent","name1"))
    
        sock.connect()

        received = None
        
        for _ in range(inifile.getint("game","num")):
            received = main(sock=sock, inifile=inifile, received=received, name=inifile.get("agent","name1"))
        
        sock.close()

        if not inifile.getboolean("connection","keep_connection"):
            break
