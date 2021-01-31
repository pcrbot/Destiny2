from . import *

help_d2_link = """
《最推荐的是使用Steam64位ID进行绑定，一次到位》
【d2绑定steam】通过Steam64位ID（游戏内/id组队码）进行账号绑定
【d2搜索玩家】通过昵称搜索命运2玩家
【d2绑定玩家】从搜索玩家返回的结果里找到待绑账号对应的序号
【d2查看绑定】查看当前QQ号所绑定的命运2玩家信息
《d2搜索玩家》返回的搜索结果序号支持直接进行的操作有：
【elo】【d2pvpstat】【d2添加乐子】【d2rr】【steamid查询】【d2绑定玩家】
仅需在这些指令后面加上序号即可，例如"elo1"
""".strip()

help_steam = """
【steamid查询】steamid转换查询 支持steamID64,steamID3,steamID或自定义url
【steam玩家搜索】通过steam昵称搜索玩家（仅限命运2玩家）
【steam展柜生成】未实装
""".strip()

help_d2_boardcast = """
【启用/禁用 d2-xur-bc】启用每周六凌晨1点05分xur信息自动推送服务
【启用/禁用 d2-too-bc】启用每周六凌晨1点05分试炼信息自动推送服务
""".strip()

help_d2_stat = """
【elo<@Steam64><#赛季序号>】查看对应玩家的ELO详情
【d2pvpstat<Steam64/Destiny2ID><详/略>】查看对应玩家的PVP战绩
【d2toostat】查看对应玩家试炼战绩 未实装
【d2来点乐子】屁威屁乐子列表 未实装
【d2添加乐子 Steam64位ID】未实装
【d2rr】RaidReport 未实装
""".strip()

help_d2_query = """
【xur<简/繁>】查看当前xur位置以及售卖装备
【试炼情报/试炼周报】查看当前试炼地图及奖励
【d2赛季结束】查看当前赛季剩余时长
【d2传说遗失】查看今天传说/大师遗失区域和掉落装备部位
【来点传说故事<简/繁>】随机来一份传说故事 未实装
""".strip()

@sv.on_fullmatch(('d2帮助','d2菜单','命运2帮助','命运2菜单'))
async def d2_help(bot, ev):
    msg = f'''
《命运2功能使用说明》
<>内为非必填参数
=============
- Steam相关 -
=============
{help_steam}
=============
- d2绑定相关 -
=============
{help_d2_link}
=============
- d2定时推送 -
=============
{help_d2_boardcast}
=============
- d2战绩相关 -
=============
{help_d2_stat}
=============
- d2查询相关 -
=============
{help_d2_query}
=============
'''.strip()
    await bot.send(ev, msg)

@sv.on_fullmatch(('d2绑定帮助','d2玩家绑定帮助'))
async def d2_player_link_help(bot, ev):
    msg = help_d2_link
    await bot.send(ev, msg)

@sv.on_fullmatch(('d2广播帮助','d2推送帮助'))
async def d2_player_link_help(bot, ev):
    msg = help_d2_boardcast
    await bot.send(ev, msg)