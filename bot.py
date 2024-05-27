# created by wjz!
# https://aiocqhttp.nonebot.dev/module/aiocqhttp/#aiocqhttp.Event.sub_type
# 上面是aiocqhttp的文档
# APEX API Key= e26077970fc92f0bede1d39836986cfb

from aiocqhttp import CQHttp, Event
from aiocqhttp.message import escape
import urllib3
import os
# 下面是自己的模块
from bot_module import antiAD

# 反向代理url=http://us.hytale.cool:2023/api/generate
# 使用方法，headers里面加一个site属性，site是目标网站的域名，比如www.baidu.com


res_path = os.path.abspath(os.path.dirname(__file__)) + '\\resources'

BOT_ID = 106674994  # 机器人的QQ号1916688982
ADMIN = 1524550199	# 
GROUP_ID=0          #

bot = CQHttp(api_root='http://127.0.0.1:5700')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
urllib3.disable_warnings()  # 关闭错误报告，因为request请求会检查ssl，验证失败会终止请求

antiAD.run(bot,[GROUP_ID]) #反广告功能



@bot.on_message("group")
async def _(event: Event):
    if (event.message.startswith("查询群友")):
        qid=event.message[4:]
        content=await bot.get_group_member_info(group_id=event.group_id,user_id=int(qid))
        print(event.group_id)
        await bot.send(event,str(content))
        

@bot.on_message("group")
async def _(event: Event):
    if (event.message.startswith("获取群聊信息")):
        await bot.send(event, str(await bot.get_group_info(group_id=event.group_id, no_cache=True, self_id=BOT_ID)))

    if (event.message == "获取我的信息"):
        await bot.send(event, await bot.get_stranger_info(user_id=event.user_id, no_cache=True, self_id=BOT_ID))




#🐱———————————获取图片的CQ码———————————————🐱
"""[CQ:image,file=https://xxxxx]"""
@bot.on_message("group")
async def _(event:Event):
    if event.message.startswith("图片CQ".lower()) and event.user_id==ADMIN:
        return await bot.send(event,escape(event.message))#对CQ码进行去转义


# ____________________下面是加好友和处理群邀请功能内容板块__________________________
@bot.on_request("friend")
async def friend_request(event: Event):
    await bot.set_friend_add_request(flag=event.flag, approve=True)


@bot.on_request("group")
async def group_request(event: Event):
    if (event.user_id != 1369727119 and event.group_id == 120457749):
        # await bot.set_group_add_request(flag=event.flag, approve=False,reason='不好意思，因为进太多群有风控风险，想拉群请联系主人哦！')
        await bot.send(event, '欢迎加入！这里是WJZ的机器人聊天群喵！(=^ ◡ ^=)', at_sender=True)


bot.run(host='127.0.0.1', port=8080)
