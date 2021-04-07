import sys
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from plugins import load_plugins
import asyncio
from plugins._utils.env import env

def main():
    loop = asyncio.get_event_loop()
    bcc = Broadcast(loop=loop)
    app = GraiaMiraiApplication(
        broadcast=bcc,
        connect_info=Session(
            host="http://xqh.ma:12321", # 填入 httpapi 服务运行的地址
            authKey="ltrump923429", # 填入 authKey
            account=3218088431, # 你的机器人的 qq 号
            websocket=True # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
        )
    )
    env['app']=app
    env['bcc']=bcc
    load_plugins()
    app.launch_blocking()

if __name__ == '__main__':
    # if len(sys.argv) >= 2:
    main()
    # else:
        # print(f'Usage: python3 {sys.argv[0]} mirai://localhost:8080/ws?authKey=$authKey&qq=$qq\n\n'
              # 'Visit https://mirai-py.originpages.com/tutorial/hello-world.html#hello-world-2 for more details.')
        # exit(1)
