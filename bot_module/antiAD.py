from aiocqhttp import CQHttp, Event

KEYWORDS=['勤工俭学','学习资料','校园墙','万能墙','兼职','临时工']

def antiAD(bot:CQHttp,groups:list[int]):
    """遇到广告关键字立刻撤回"""
    @bot.on_message("group")
    async def _(event:Event):
        if (keyword in event.message for keyword in KEYWORDS) and event.group_id in groups:
            await bot.delete_msg(event.message_id)#撤回消息
            await bot.set_group_kick(event.group_id,event.user_id,reject_add_request=True)#踢人
            await bot.send(event,"检测到发广告，已撤回并踢出")

def run(bot:CQHttp,groups):
    antiAD(bot,groups)
    print("启动反广告功能")