from ..D2_API import *
#from ..player_search import *
from .translate import get_rewards_translation

import hoshino
from hoshino import Service, logger, aiorequests

import json, datetime, calendar

sv = Service("d2-too")
svbc = Service("d2-too-bc", enable_on_default=False)

@sv.on_fullmatch(("试炼情报","too情报","d2too情报","d2试炼情报","试炼周报","too周报"))
async def d2_send_trail_detail_thisweek(bot, ev):
    info = await get_trail_detail_msg()
    if "errmsg" in info.keys():
        msg = info["errmsg"]
    else:
        msg = info["msg"]
    await bot.send(ev, msg)

async def get_trail_detail_msg(weekNumber=0, language=DEFAULT_LANGUAGE):
    url = f"https://api.trialsofthenine.com/weeks/{weekNumber}"
    resp = await aiorequests.get(url, proxies=PROXIES, timeout=5)
    data = await resp.json()
    try:
        info = {}
        week_number = data["weekNumber"]
        end_date = data["endDate"]
        rest_time_data = get_trail_rest_time(end_date)
        if not rest_time_data["is_now"]:
            info["msg"] = rest_time_data["msg"]
            return info
        map_name = data["map"]["name"]
        map_img = "https://www.bungie.net" + data["map"]["imagePath"]
        rewards = {}
        rewards['three_wins'] = {'name':data["rewards"]["threeWins"]}
        rewards['five_wins'] = {'name':data["rewards"]["fiveWins"]}
        rewards['seven_wins'] = {'name':data["rewards"]["sevenWins"]}
        rewards['flawless'] = {'name':data["rewards"]["flawless"]}
        rewards['mod'] = {'name':data["rewards"]["mod"]}
        rewards = get_rewards_translation(rewards, language)
        info["msg"] = f"""
第{week_number}周试炼情报
{rest_time_data["msg"]}
地图：{map_name}
三胜奖励：{rewards['three_wins']['ts_name']}
[CQ:image,file={rewards['three_wins']['icon_url']}]
五胜奖励：{rewards['five_wins']['ts_name']}
[CQ:image,file={rewards['five_wins']['icon_url']}]
七胜奖励：{rewards['seven_wins']['ts_name']}
[CQ:image,file={rewards['seven_wins']['icon_url']}]
无暇奖励：{rewards['flawless']['ts_name']}
[CQ:image,file={rewards['flawless']['icon_url']}]
专家模组：{rewards['mod']['ts_name']}
[CQ:image,file={rewards['mod']['icon_url']}]
[CQ:image,file={map_img}]
        """.strip()
    except aiorequests.Timeout as e:
        info["errmsg"] = f"查询超时，请重试"
    except Exception as e:
        info["errmsg"] = f"查询试炼情报出错，错误原因为{e}"
    return info

def get_trail_rest_time(date):
    data = {}
    now_time = datetime.datetime.now()
    date_zh = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
    next_trail = date_zh + datetime.timedelta(days=4)
    if now_time < date_zh:
        delta = date_zh - now_time
        data["msg"] = f"距离本周试炼结束还有{delta.days}天{delta.seconds//3600}时{delta.seconds//60%60}分"
        data["is_now"] = True
    else:
        delta = next_trail - now_time
        data["msg"] = f"距离下一次试炼开始还有{delta.days}天{delta.seconds//3600}时{delta.seconds//60%60}分哦~"
        data["is_now"] = False
    return data