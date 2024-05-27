from aiocqhttp import CQHttp, Event
import os
import json
import asyncio
import datetime

# 目录路径
res_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "\\resources"
file_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

GROUP_ID: int = None    #点餐群号
START_TIME = "00:00"
END_TIME = "00:00"
CAN_ORDER = False       #是否可以点餐
MENU:dict=None          #菜单列表
MENU_PICTURE:str=''
ORDER_NUMBER = 1        #当天的点餐订单总序号

bot = CQHttp("嘻嘻哈哈")


with open(res_path + r"\food_menu.json", encoding="utf-8") as file:
    MENU: dict = json.load(file)  # 获取菜单

class Order:
    """订单类，包含菜品名、"""
    def __init__(
        self, dish: str, price:int, qq_number: int, order_number: int, shop_name: str, tips:str
    ) -> None:
        self.dish = dish
        self.qq_number = qq_number
        self.order_number = order_number
        self.shop_name = shop_name
        self.tips=tips
        self.price=price
        pass

    def getOrderInfo(self):
        return f"订单信息：\n订单号：{self.order_number}\n店铺名：{self.shop_name}\
            \n菜品名和价格：{self.dish}：{self.price}\n\n点单QQ号：{self.qq_number}"+\
            (f"\n备注：{self.tips}" if self.tips else '')

ALL_ORDER:list[Order]=[]            #存储当前点单的所有序号


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
            if dish_price: return ("FIND_SUCCESS",0,shop_name)
            return ("DISH_NOT_FOUND",0,shop_name)#价格是0，说明没找到这个菜
    return ("SHOP_NOT_FOUND",0,shop_name)



def check_order(user_id:int):
    """用户查询点单功能,返回属于这个用户的点单"""
    user_order=[]
    for order in ALL_ORDER:
        if order.qq_number==user_id:
            user_order.append(order)
    return user_order

def register_help_menu():
    """查询帮助菜单"""
    

def register_check_order():
    """实现群内用户查询点餐功能"""
    @bot.on_message("group")
    async def _(event: Event):
        if event.message == "我的单号":
            user_order=check_order(event.user_id)
            if not user_order:
                return await bot.send(event,"你还没有点单哦！(｡･∀･)ﾉﾞ",at_sender=True)
            for order in user_order:#如果有多个点餐信息，我们打印出来
                await bot.send(event,order.getOrderInfo(),at_sender=True)
                await asyncio.sleep(0.3)
            return


def register_meal_ordering():
    """实现群内用户的点餐功能"""
    @bot.on_message("group")
    async def _(event: Event):
        if event.group_id == GROUP_ID:
            if event.message.startswith("点餐"):  # 触发点餐条件
                now = datetime.datetime.now()
                
                if now.weekday() >= 5:  # 周六周日不点餐
                    return await bot.send(event, "周末不点餐嘞!(ノ≧∀≦)ノ ミ ┻━┻", at_sender=True)

                if event.message == "点餐":  # 没说点什么
                    return await bot.send(event,"你要点什么呢？(｡･∀･)ﾉﾞ\n输入菜单来获取点餐列表\n\
                        点餐示例: 点餐 1 香菇滑鸡饭",at_sender=True)
                    
                order_messages:list=event.message[2:].split(' ')# 1 香菇滑鸡饭 不要辣
                result_tuple=find_dish(order_messages)
                match result_tuple[0]:
                    
                    case "SHOP_NOT_FOUND":
                        return await bot.send(event,"没有这个序号的店哦！请重新点餐！(つД`)ノ\n示例1:\n\
                            点餐 1 香菇滑鸡饭\n示例2:\n点餐 1 香菇滑鸡饭 不要辣",at_sender=True)
                        
                    case "DISH_NOT_FOUND":
                        return await bot.send(event,"这个店没有这个菜哦！请重新点餐！(ㄒoㄒ)", at_sender=True)
                    
                    case "FIND_SUCCESS":#成功找到了，下面应该创建订单
                        new_order=Order(order_messages[1],result_tuple[1],
                        event.user_id,ORDER_NUMBER,result_tuple[2],
                        order_messages[2] if len(order_messages)>2 else '')
                        
                        global ALL_ORDER
                        global ORDER_NUMBER
                        
                        ALL_ORDER.append(new_order)
                        ORDER_NUMBER=ORDER_NUMBER+1
                        print(new_order.getOrderInfo())#顺便打印出来看看
                        
                        return await bot.send(event,"点餐成功！٩(≧▽≦*)o\n\
                        你的单号：" + ORDER_NUMBER + "\\n请记得取餐哦！",at_sender=True)
                


                

                



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
