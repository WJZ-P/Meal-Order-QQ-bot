from aiocqhttp import CQHttp, Event,MessageSegment
import os
import json
import asyncio
import datetime
from collections import defaultdict
import schedule
import time
import threading
# 目录路径
res_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "\\resources"
file_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
BOT_ID=1524550199       #从外面传入的bot机器人ID
GROUP_ID: int = 543613447    #点餐群号543613447 测试群是801275394
START_TIME = "09:00"
END_TIME = "11:30"
CAN_ORDER = False       #是否可以点餐
MENU={}                 #菜单列表
MENU_PICTURE:str='https://article.biliimg.com/bfs/new_dyn/cc30ea15979e9e46cb70b598a948c38f39684091.png'     #图片的路径
ORDER_NUMBER = 0        #当天的点餐订单总序号
XIAOLE_ID=1451919350    #小乐姐姐ID
bot = CQHttp("嘻嘻哈哈")

class Order:
    """订单类，包含菜品名、"""
    def __init__(
        self, dish: str, price:int, qq_number: int, order_number: int, shop_name: str, tips:str
    ) -> None:
        self.dish = dish                    #菜品名
        self.qq_number = qq_number          #QQ号
        self.order_number = order_number    #订单号
        self.shop_name = shop_name          #店家名字
        self.tips=tips                      #备注
        self.price=price                    #餐品价格
        pass

    def getOrderInfo(self):
        return f"订单信息：\n订单号：{self.order_number}\n店铺名：{self.shop_name}\
            \n菜品名：{self.dish}：{self.price}元\n点单QQ号：{self.qq_number}"+\
            (f"\n备注：{self.tips}" if self.tips else '')
            
    def getOrderInfo_simple(self):
        return f"单号:{self.order_number}:￥{self.price}" + (f" (备注: {self.tips})  " if self.tips else '  ')       

ALL_ORDER:list[Order]=[]            #存储当前的所有点单

def get_menu():
    """更新菜单"""
    global MENU
    with open(res_path + r"\food_menu.json", encoding="utf-8") as file:
        MENU = json.load(file)  # 获取菜单

def find_dish(order_messages:list)->tuple:  
    """根据输入信息找到对应餐品，输入信息 0为店家序号
    
    返回的是(查询信息,餐品价格,店家名字)
    其中查询信息有
     "FIND_SUCCESS"  "DISH_NOT_FOUND" "SHOP_NOT_FOUND"
    """
    #下面在菜单里找到餐品
    order_dish=order_messages[1]      # 点的菜品
    shop_num=order_messages[0] + '.'  # 店家序号后加上点号
    shop_name=''
    for shop in MENU:
        if shop.startswith(shop_num):#找到了对应的店家
            shop_name=shop.split('.')[1]
            dish_price = MENU[shop].get(order_dish,0)#查找价格
            if dish_price: return ("FIND_SUCCESS",dish_price,shop_name)
            return ("DISH_NOT_FOUND",0,shop_name)#价格是0，说明没找到这个菜
    return ("SHOP_NOT_FOUND",0,shop_name)



def check_order(user_id:int):
    """用户查询点单功能,返回属于这个用户的点单"""
    user_order=[]
    for order in ALL_ORDER:
        if order.qq_number==user_id:
            user_order.append(order)
    return user_order

def print_order_list():
    """打印出点单列表"""
    
    total_message=[f'今天共有{len(ALL_ORDER)}个订单:']#存储每一家店铺的点单信息列表
    # 按店铺名组织订单
    order_shop_today=[]#今天的订单中一共几家店被点了，需要排序
    for order in ALL_ORDER:
        if order.shop_name not in order_shop_today:
            order_shop_today.append(order.shop_name)
            
    #   接下来我们需要对店铺名字进行排序
    sorted_order_shop_today={}
    for shop_name in MENU:
        if shop_name.split('.')[1] in order_shop_today:
            sorted_order_shop_today[shop_name]=[]#这里的shop_name类似   1.大米兄弟
            
    #现在排序已经完成，接下来我们需要按照店家名字来组织订单
    for shop_name in sorted_order_shop_today:   #[大米兄弟,卫子夫]
        order_of_this_shop={}#每一家店的所有订单
        for order in ALL_ORDER:
            if order.shop_name== shop_name.split('.')[1]:#大米兄弟 == 大米兄弟  找到了属于这家店的菜了！
                if order.dish not in order_of_this_shop:
                    order_of_this_shop[order.dish]=[order]#把是某个菜品的所有order都放进来！    
                    #如1.大米兄弟{'香菇牛肉饭':[object:order]}
                else: order_of_this_shop[order.dish].append(order)
        
        #上面已经插入了所有的信息啦！接下来要转成字符串
        message= shop_name+'\n'  #"如:1.大米兄弟"
        for dish in order_of_this_shop:
            message+='\t'+dish+f':共{len(order_of_this_shop[dish])}人\n\t\t'
            for order in order_of_this_shop[dish]:
                message+=order.getOrderInfo_simple()
            message+='\n'
        
        total_message.append(message)#插入信息
        
    return '\n'.join(total_message)#返回所有信息


def register_help_menu():
    """查询帮助菜单"""
    @bot.on_message("group")
    async def _(event: Event):
        if event.group_id==GROUP_ID:
            if event.message == "帮助" or str(BOT_ID) in event.message:#需要发送帮助菜单
                return await bot.send(event,"输入“菜单”来获取点餐列表\
                \n输入“我的单号”来获取你的点餐单号\n输入“取消点餐”来取消你的所有订单！\
                \n管理员输入“单号查询+订单号”可查询点单用户\n输入点餐 店名序号 菜名 备注(可选)来点餐\
                        \n示例：\n点餐 1 香菇滑鸡饭 不要鸡不要饭",
                                      at_sender=True)

            if event.message=='菜单':
                return await bot.send(event, MessageSegment.image(MENU_PICTURE))



def register_check_order():
    """实现群内用户查询点餐功能"""
    @bot.on_message("group")
    async def _(event: Event):
        if event.message == "我的单号" and event.group_id==GROUP_ID:
            user_order=check_order(event.user_id)
            if not user_order:
                return await bot.send(event,"你还没有点单哦！(｡･∀･)ﾉﾞ",at_sender=True)
            for order in user_order:#如果有多个点餐信息，我们打印出来
                await bot.send(event,f'下面是你的点单！[CQ:at,qq={event.user_id}]\n'+order.getOrderInfo())
                await asyncio.sleep(0.3)
         
        if event.message.startswith("单号查询") and event.group_id==GROUP_ID and (event.user_id==1369727119 or event.user_id==XIAOLE_ID):
            order_numbers=event.message[4:].strip().split(' ')
            has_find=False
            for order_need_to_check in order_numbers:
                for order in ALL_ORDER:
                    if order.order_number==int(order_need_to_check):
                        has_find=True
                        await bot.send(event,order.getOrderInfo()+f'\n点单同学：[CQ:at,qq={order.qq_number}]')
            if not has_find:
                return await bot.send(event,"没有这个订单号哦！(つД`)ノ",at_sender=True)


def register_meal_ordering():
    """实现群内用户的点餐功能"""
    @bot.on_message("group")
    async def _(event: Event):
        if event.group_id == GROUP_ID:
            if event.message.startswith("点餐"):  # 触发点餐条件
                if not CAN_ORDER:
                    return await bot.send(event,f'现在还不是点餐时间哦！点餐时间是{START_TIME}-{END_TIME}',at_sender=True)
                now = datetime.datetime.now()
                if now.weekday() >= 5:  # 周六周日不点餐
                    return await bot.send(event, "周末不点餐嘞!(ノ≧∀≦)ノ ミ ┻━┻", at_sender=True)

                if event.message == "点餐":# 没说点什么
                    return await bot.send(event,"你要点什么呢？(｡･∀･)ﾉﾞ\n输入菜单来获取点餐列表\n\
                        点餐示例: 点餐 1 香菇滑鸡饭",at_sender=True)
                    
                nums_index=0
                message=event.message[2:].strip()
                while message[nums_index].isdigit():  # 获取序号
                    nums_index += 1
                    
                order_messages=[]
                order_messages.append(message[:nums_index])  # 序号
                order_messages += message[nums_index:].strip().split(" ")  # 香菇滑鸡饭 备注（可选）
                
                result_tuple=find_dish(order_messages)#(店家序号 菜品名 备注)
                print(result_tuple)
                match result_tuple[0]:
                    
                    case "SHOP_NOT_FOUND":
                        return await bot.send(event,"没有这个序号的店哦！请重新点餐！(つД`)ノ\n示例1:\n\
                            点餐 1 香菇滑鸡饭\n示例2:\n点餐 1 香菇滑鸡饭 不要辣",at_sender=True)
                        
                    case "DISH_NOT_FOUND":
                        return await bot.send(event,"这家店没有这个菜哦！请重新点餐！(ㄒoㄒ)\n注意写备注的话要和菜品名之间隔开空格哦！", at_sender=True)
                    
                    case "FIND_SUCCESS":#成功找到了，下面应该创建订单
                        global ORDER_NUMBER
                        ORDER_NUMBER=ORDER_NUMBER+1
                        new_order=Order(order_messages[1],result_tuple[1],
                        event.user_id,ORDER_NUMBER,result_tuple[2],
                        order_messages[2] if len(order_messages)>2 else '')
                        
                        global ALL_ORDER
                        ALL_ORDER.append(new_order)
                        print(new_order.getOrderInfo())#顺便打印出来看看
                        
                        return await bot.send(event,"点餐成功！٩(≧▽≦*)o\
                        \n你的单号：" + str(ORDER_NUMBER) + f'\n店家：{new_order.shop_name}'+f'\n菜品：{new_order.dish}：{new_order.price}'+"\
                        \n请记得在12:00-12:30到对应的档口按号取餐哦！(取餐时付款)",at_sender=True)
                        
def register_cancel_order():
    """实现群内用户取消点餐功能"""
    @bot.on_message("group")
    async def _(event: Event):
        if (event.message=='取消点餐' or event.message=="取消订单") and event.group_id==GROUP_ID:
            have_order=False
            global ALL_ORDER
            new_all_order=[]
            for order in ALL_ORDER:
                if order.qq_number==event.user_id:#找到了这个人的点餐订单
                    have_order=True
                    print(f"删除掉订单{order.order_number}")
                else: new_all_order.append(order)
            ALL_ORDER=new_all_order
            if have_order:
                return await bot.send(event,f"已取消你的所有点餐！(◕‿◕❀)[CQ:at,qq={event.user_id}]")
            return await bot.send(event,"你没有点餐我取消啥?(=^-ω-^=)",at_sender=True)
                
def start_ordering(bot: CQHttp):
    """开始点餐"""
    
    async def _(bot: CQHttp):
        print("开始点餐")
        global CAN_ORDER
        global ORDER_NUMBER
        global ALL_ORDER
        ALL_ORDER=[]
        ORDER_NUMBER = 0  # 点餐序号重置
        CAN_ORDER = True
        get_menu()  # 每次开始点餐，更新菜单
        print("点餐开始了！下面在群里发送信息")
        #await bot.send_group_msg(group_id=int(GROUP_ID),message="可以点餐啦！")

        asyncio.create_task(bot.send_group_msg(group_id=int(GROUP_ID),#[CQ:at,qq=all]
                                               message="[CQ:at,qq=all]点餐开始了哦！(✪ω✪)\n点餐格式：\n点餐 店名序号 菜名 备注(可选)\n示例：\n点餐 1 香菇滑鸡饭 不要辣" + MessageSegment.image(
                                                   MENU_PICTURE)+"\n输入“我的单号”来查看取餐号\n输入“菜单”显示菜单\n输入“帮助”来查看指令\n命令都不需要加前缀哦！\n\
                                                    \n注意点餐是我们快乐食间的档口点餐，不是外卖哦！店家需要备餐时间，请在十二点后到档口取餐并付款嘞！" + MessageSegment.image(
                                                   "https://article.biliimg.com/bfs/article/6691afe19dfe408500d6fadb750a7bc039684091.gif")))  # 猫娘炒饭
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
        asyncio.create_task(bot.send_msg(user_id=BOT_ID, message=order_list))   #发送一份给机器人自己
        await asyncio.sleep(1)
        asyncio.create_task(bot.send_msg(user_id=1369727119, message=order_list))   #发送一份给我
        await asyncio.sleep(1)
        asyncio.create_task(bot.set_group_card(group_id=int(GROUP_ID), user_id=BOT_ID, card="快乐食间外带点餐员(ฅ^ω^ฅ)"))  
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
                    f"欢迎加入快乐食间外带点餐群！\n周一到周五{START_TIME}点到{END_TIME}可以外带点餐哦！٩(ˊᗜˋ*)و ",
                    at_sender=True,
                )
            )

def time_trigger(bot: CQHttp):
    def _():
        time_schedule = schedule.Scheduler()
        #下面是周一到周五点餐的触发器
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
        #周末不点餐
        # time_schedule.every().day.at(START_TIME).do(start_ordering, bot)    #每天这个时候都出发
        # time_schedule.every().day.at(END_TIME).do(stop_ordering, bot)       #每天都触发s
        while True:
            time_schedule.run_pending()
            time.sleep(5)

    threading.Thread(target=_).start()

def run(mybot:CQHttp):
    """启动服务"""
    global bot
    bot=mybot       #设置bot
    register_cancel_order() #取消点餐
    register_check_order()  #我的单号
    register_help_menu()    #查看菜单
    register_meal_ordering()#点餐功能
    register_new_member_welcome(bot)#欢迎新成员加入
    print("重庆师范大学——点餐系统启动！")
    get_menu()
    time_trigger(bot)   #开启时间触发器