from mirai import Mirai, FriendMessage, GroupMessage, MessageChain

from .._utils import at_me, Sender, Type, reply

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

helpMsg = """
"""

@sub_app.receiver(FriendMessage)
@sub_app.receiver(GroupMessage)
async def show_help(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    app_reply = reply(app, sender, event_type)

    keywords = ['.help', '。help', '使用帮助']
    text = message.toString().strip().lower()
    if (text in keywords) or (at_me(app, message) and any(keyword in text for keyword in keywords)):
        await app_reply(helpMsg)
