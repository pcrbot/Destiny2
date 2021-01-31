import hoshino
from hoshino import Service, R

sv = Service("d2-query")

@sv.on_fullmatch(('d2菜谱','d2食谱','曙光节配方','d2配方','黎明日配方','烤箱菜谱','烤箱食谱','饼干配方','d2饼干','老八秘制小饼干'))
async def d2_query_dawning_menu(bot, ev):
    pic = R.img('destiny2/query/dawning/menu.jpg').cqcode
    await bot.send(ev, pic)