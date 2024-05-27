from aiocqhttp import CQHttp, Event
import traceback

bot=1

def wrapped_event_handler(handler, bot:CQHttp,Qid:int):
    async def wrapper(event: Event):
        try:
            return await handler(event)
        except Exception as e:
            print(e)
            # send error msg and stack trace to qq
            await bot.send_msg(user_id=Qid,message=traceback.format_exc())
    return wrapper


def reg_error_handler(bot:CQHttp,Qid:int):
    """注册错误处理器，用来给所有的注册函数加上try except块\nQid为错误报告接受者QQ，通常为作者"""
    orig_on_message = bot.on_message
    def handler(*args):
        def wrapper(fn):#这里的fn就是@下面的那个函数
            orig_on_message(*args)(wrapped_event_handler(fn, bot,Qid))#后面的函数就是本来@修饰符下面定义的一个函数，这里套一个壳子
            #左边是装饰器，返回一个wrapper。右边是被装饰的函数
        return wrapper

    bot.on_message = handler

