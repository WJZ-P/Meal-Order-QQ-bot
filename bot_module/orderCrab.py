import asyncio
import datetime
import json
import os
import threading
import time

import schedule
from aiocqhttp import CQHttp, Event, MessageSegment

# 目录路径
res_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "\\resources"
file_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BOT_ID = 1916688982  # 从外面传入的bot机器人ID
GROUP_ID: int = 934773893  # 点餐群号543613447 测试群是801275394
START_TIME = "09:00"
END_TIME = "17:00"
CAN_ORDER = False  # 是否可以点餐
MENU = {}  # 菜单列表
MENU_PICTURE: str = res_path + '\\大闸蟹.png'  # 图片的路径
ORDER_NUMBER = 0  # 当天的点餐订单总序号
XIAOLE_ID = 1451919350  # 小乐姐姐ID
bot = CQHttp("嘻嘻哈哈")


class Order:
    """订单类，包含菜品名、"""

    def __init__(
            self, qq_number: int, order_number: int, stu_name: str, collage: str, phone_num: str, order_pick_time: str
    ) -> None:
        self.qq_number = qq_number  # QQ号
        self.order_number = order_number  # 订单号
        self.stu_name = stu_name
        self.collage = collage  # 订购者的学院
        self.order_pick_time = order_pick_time
        self.phone_num = phone_num
        pass


ALL_ORDER: list[Order] = []  # 存储当前的所有大闸蟹订单


def register_help_menu():
    """查询帮助菜单"""

    @bot.on_message("group")
    async def _(event: Event):
        if event.group_id == GROUP_ID:
            if event.message == "帮助" or str(BOT_ID) in event.message:  # 需要发送帮助菜单
                return await bot.send(event, MessageSegment.image(MENU_PICTURE) + "\n每天09：00-17：00可以下单第二天的大闸蟹哦！\n"
                                      + "下单请按如下格式：\n下单 姓名 学院 联系电话 取餐时间（中午\\晚上）\n例：\n下单 王小明 计算机学院 1337656XXXX 中午"
                                        "\n输入“取消下单”来取消下单的大闸蟹。",
                                      at_sender=True)


def register_meal_ordering():
    """实现群内用户的点餐功能"""

    @bot.on_message("group")
    async def _(event: Event):
        global ORDER_NUMBER
        if event.group_id == GROUP_ID:
            if event.message.startswith("下单"):  # 触发点餐条件
                if not CAN_ORDER:
                    return await bot.send(event, f'现在还不是下单时间哦！点餐时间是{START_TIME}-{END_TIME}',
                                          at_sender=True)
                now = datetime.datetime.now()
                if now.weekday() >= 5:  # 周六周日不点餐
                    return await bot.send(event, "周末不下单嘞!(ノ≧∀≦)ノ ミ ┻━┻", at_sender=True)

                if event.message.strip() == "下单":  # 没说点什么
                    return await bot.send(event, "信息不全哦？(｡･∀･)ﾉﾞ\n例：\n\
                        下单 王小明 计算机学院 1337656XXXX 中午", at_sender=True)
                # 下面开始准备点餐
            order_infos = event.message[2:].strip().split(" ")  # 点单信息，分别是 姓名 学院 电话 取餐时间
            if len(order_infos) < 4 or order_infos[3] != "中午" or order_infos[3] != "晚上":  # 信息不全
                return await bot.send(event,
                                      "信息不全哦？(｡･∀･)ﾉﾞ\n例：\n下单 王小明 计算机学院 1337656XXXX 中午\\晚上(字要对的上哦，只能是中午或晚上)")

            ORDER_NUMBER += 1  # 订单序号加1
            ALL_ORDER.append(
                Order(event.user_id, ORDER_NUMBER, order_infos[0], order_infos[1], order_infos[2], order_infos[3]))
            return_message = f"成功预定大闸蟹！请耐心等待大闸蟹的到来！(◕‿◕❀)\n"

            # 下面输出接龙列表
            for order in ALL_ORDER:
                return_message += f"订单{order.order_number}：{order.stu_name}({order.collage}) 电话：{order.phone_num} 取餐时间：{order.order_pick_time}\n"

            return await bot.send(event, return_message.strip(), at_sender=True)


def print_order_list():
    global ALL_ORDER
    noon_order = []
    night_order = []
    for order in ALL_ORDER:
        if order.order_pick_time == "中午":
            noon_order.append(order)
        else:
            night_order.append(order)
    result_msg = "今日的大闸蟹订单如下：\n中午拿蟹订单："

    # 下面先添加中午的订单列表
    for order in noon_order:
        result_msg += f"订单{order.order_number}：{order.stu_name}({order.collage}) 电话：{order.phone_num}\n"
    result_msg += "晚上拿蟹订单："

    for order in night_order:
        result_msg += f"订单{order.order_number}：{order.stu_name}({order.collage}) 电话：{order.phone_num}\n"
    return result_msg.strip()


def register_cancel_order():
    """实现群内用户取消点餐功能"""

    @bot.on_message("group")
    async def _(event: Event):
        if (event.message == '取消下单' or event.message == "取消订单") and event.group_id == GROUP_ID:
            have_order = False
            global ALL_ORDER
            new_all_order = []
            for order in ALL_ORDER:
                if order.qq_number == event.user_id:  # 找到了这个人的点餐订单
                    have_order = True
                    print(f"删除掉订单{order.order_number}")
                else:
                    new_all_order.append(order)
            ALL_ORDER = new_all_order
            if have_order:
                return await bot.send(event, f"你的大闸蟹回去喽！(◕‿◕❀)[CQ:at,qq={event.user_id}]")
            return await bot.send(event, "你没有点餐我取消啥?(=^-ω-^=)", at_sender=True)


def start_ordering(bot: CQHttp):
    """开始点餐"""

    async def _(bot: CQHttp):
        print("开始点餐")
        global CAN_ORDER
        global ORDER_NUMBER
        global ALL_ORDER
        ALL_ORDER = []
        ORDER_NUMBER = 0  # 点餐序号重置
        CAN_ORDER = True
        print("点餐开始了！下面在群里发送信息")
        # await bot.send_group_msg(group_id=int(GROUP_ID),message="可以点餐啦！")

        asyncio.create_task(bot.send_group_msg(group_id=int(GROUP_ID),  # [CQ:at,qq=all]
                                               message="[CQ:at,qq=all]可以下单大闸蟹了哦！(✪ω✪)\n下单格式：\n下单 王小明 计算机学院 1337656XXXX 中午\n" + MessageSegment.image(
                                                   MENU_PICTURE)))  # 猫娘炒饭
        # asyncio.create_task(bot.send_group_msg(group_id=int(GROUP_ID),
        #    message="[CQ:at,qq=all]点餐开始了哦！(✪ω✪)\n点餐格式：\n点餐 店名序号 菜名 备注(可选)\n示例：\n点餐 1 香菇滑鸡饭 不要辣"+ MessageSegment.image(
        #                                     "https://article.biliimg.com/bfs/article/6691afe19dfe408500d6fadb750a7bc039684091.gif")))
        await asyncio.sleep(1)
        asyncio.create_task(bot.set_group_card(group_id=int(GROUP_ID), user_id=BOT_ID, card="激情点餐ing!(๑´ڡ`๑)"))

    asyncio.run(_(bot))


def stop_ordering(bot: CQHttp):
    """停止点餐,并把总订单发送给管理员"""

    async def _(bot: CQHttp):
        print("停止点餐")
        global CAN_ORDER
        CAN_ORDER = False
        order_list = print_order_list()  # 获取总的订单，下面发给管理员
        print(order_list)
        asyncio.create_task(
            bot.send_group_msg(group_id=int(GROUP_ID), message="点餐结束啦！记得到指定地点领餐哦！ (＾ｖ＾)",
                               auto_escape=False))

        # asyncio.create_task(bot.send_group_msg(group_id=865997606,message=order_list))#发一份给木桥群备案
        # await asyncio.sleep(1)
        asyncio.create_task(bot.send_msg(user_id=XIAOLE_ID, message=order_list))  # XIAOLE_ID,发送总的点餐统计消息给小乐姐姐
        await asyncio.sleep(1)
        asyncio.create_task(bot.send_msg(user_id=BOT_ID, message=order_list))  # 发送一份给机器人自己
        await asyncio.sleep(1)
        asyncio.create_task(bot.send_msg(user_id=1369727119, message=order_list))  # 发送一份给我
        await asyncio.sleep(1)
        asyncio.create_task(
            bot.set_group_card(group_id=int(GROUP_ID), user_id=BOT_ID, card="快乐食间大闸蟹点餐员(ฅ^ω^ฅ)"))
        # 改回原来的名字

    asyncio.run(_(bot))


def register_new_member_welcome(bot: CQHttp):
    """新成员入群欢迎"""

    @bot.on_request("group")  # 处理加群请求
    async def _(event: Event):
        if event.group_id == GROUP_ID:  # 快乐食间外带点餐群
            asyncio.create_task(
                bot.set_group_add_request(flag=event.flag, sub_type="add", approve=True)
            )
            print("同意了" + str(event.user_id) + "的加群请求")
            asyncio.create_task(
                bot.send(
                    event,
                    f"欢迎加入快乐食间大闸蟹下单群！\n周一到周五{START_TIME}点到{END_TIME}可以点大闸蟹哦！٩(ˊᗜˋ*)و ",
                    at_sender=True,
                )
            )


def time_trigger(bot: CQHttp):
    def _():
        time_schedule = schedule.Scheduler()
        # 下面是周一到周五点餐的触发器
        time_schedule.every().monday.at(START_TIME).do(start_ordering, bot)
        time_schedule.every().monday.at(END_TIME).do(stop_ordering, bot)
        #
        time_schedule.every().tuesday.at(START_TIME).do(start_ordering, bot)
        time_schedule.every().tuesday.at(END_TIME).do(stop_ordering, bot)
        #
        time_schedule.every().wednesday.at(START_TIME).do(start_ordering, bot)
        time_schedule.every().wednesday.at(END_TIME).do(stop_ordering, bot)
        #
        time_schedule.every().thursday.at(START_TIME).do(start_ordering, bot)
        time_schedule.every().thursday.at(END_TIME).do(stop_ordering, bot)
        #
        time_schedule.every().friday.at(START_TIME).do(start_ordering, bot)
        time_schedule.every().friday.at(END_TIME).do(stop_ordering, bot)
        # 周末不点餐
        # time_schedule.every().day.at(START_TIME).do(start_ordering, bot)    #每天这个时候都出发
        # time_schedule.every().day.at(END_TIME).do(stop_ordering, bot)       #每天都触发s
        while True:
            time_schedule.run_pending()
            time.sleep(5)

    threading.Thread(target=_).start()


def run(mybot: CQHttp):
    """启动服务"""
    global bot
    bot = mybot  # 设置bot
    register_cancel_order()  # 取消点餐
    register_help_menu()  # 查看菜单
    register_meal_ordering()  # 点餐功能
    register_new_member_welcome(bot)  # 欢迎新成员加入
    print("重庆大学——大闸蟹下单群启动！")
    time_trigger(bot)  # 开启时间触发器
