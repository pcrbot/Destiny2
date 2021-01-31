import hoshino
from hoshino import Service
from ..D2_API import *

import datetime
import pytz

sv = Service('d2-countdown')
tz = pytz.timezone('Asia/Shanghai')

from .countdown import *

@sv.on_fullmatch(('d2赛季结束','d2赛季倒计时','d2赛季剩余','d2赛季剩余时间','d2赛季时间'))
async def d2_current_season_countdown(bot, ev):
    season = await get_season_countdown(language=DEFAULT_LANGUAGE)
    msg = f"距离【{season['season_name']}】结束还有【{season['season_rest_days']}天{season['season_rest_hours']}时{season['season_rest_minutes']}分】"
    await bot.send(ev, msg, at_sender=True)
    
@sv.on_fullmatch(("传说遗失区域","大师遗失区域","传说遗落之地","大师遗落之地","d2遗失区域","d2遗落之地","d2传说遗失区域","d2大师遗失区域","d2传说遗落之地","d2大师遗落之地","d2传说遗落","d2大师遗落","d2传说遗失","d2大师遗失"))
async def d2_lost_sectors_rewards(bot, ev):
    detail = get_today_lostsectors_reward()
    msg = f"今天的传说/大师遗落之地信息如下哦~\n1250传说遗落之地：{detail['map_1250']}\n1250掉落部位：{detail['armor_1250']}\n1280大师遗落之地：{detail['map_1280']}\n1280掉落部位：{detail['armor_1280']}"
    await bot.send(ev, msg)

