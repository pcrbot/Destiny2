# 要改的 合并一下下pve和pvp 直接传参
# pvp_stats = stats_data['results']['allPvP']['allTime'] 要捕获一下错误 有可能没有alltime
import hoshino
from hoshino import Service
from ..D2_API import *
from ..player_search import *

import datetime
import pytz
import json
import requests
import os
import re
import datetime
import cloudscraper

sv = Service('d2-stat',help_='''
=========================
【elo<@Steam64><#赛季序号>】查看对应玩家的ELO详情
【d2pvpstat<Steam64/Destiny2ID><详/de>】查看对应玩家的PVP战绩(详/略)
=========================
<>内参数为非必填，默认查询当前QQ号所绑定账号，默认赛季为当前赛季
    '''.strip())
tz = pytz.timezone('Asia/Shanghai')

from .stat import *
from .trn import *

@sv.on_fullmatch(('elo帮助','d2elo帮助','d2stat帮助','d2战绩帮助','d2数据帮助'))
async def d2_stat_help(bot, ev):
    msg = '''
《ELO查询帮助》
<>内参数为非必填，默认查询当前QQ号所绑定账号，默认赛季为当前赛季
【elo查询<@Steam64><#赛季序号>】查看当前绑定账号的ELO
    '''.strip()
    await bot.send(ev, msg)

@sv.on_prefix(('d2pvpstat','d2pvp战绩','d2屁威屁战绩','d2战绩查询','d2pvp数据'))
async def d2_stat_pvp_mix(bot, ev):
    """
    stat最佳武器改成zh
    """
    uid = str(ev.user_id)
    input_text = ev.message.extract_plain_text().strip()
    msg_stat = await d2_stat_pvp_stat(uid=uid,input_text=input_text,no_name=False)
    msg_elo = await d2_stat_trn_elo(user_id=uid, arg=input_text,no_name=True)
    msg = msg_stat + '\nELO:\n' + msg_elo
    await bot.send(ev, msg)

@sv.on_prefix(('d2pvpkd','d2pvpkda'))
async def d2_stat_pvp_simple(bot, ev):
    uid = str(ev.user_id)
    input_text = ev.message.extract_plain_text().strip()
    msg_stat = await d2_stat_pvp_stat(uid=uid,input_text=input_text)
    await bot.send(ev, msg_stat)

@sv.on_prefix(('elo查询','elo','d2elo'))
async def d2_stat_elo_detail(bot, ev):
    user_id = ev.user_id
    arg = ev.message.extract_plain_text().strip()
    msg = await d2_stat_trn_elo(user_id, arg)
    await bot.send(ev, msg)

async def d2_stat_pvp_stat(uid, input_text='', no_name=False):
    """
    返回固定格式pvp基础数据消息文本
    """
    if not input_text:
        stats_data = await get_pvp_general_historical_stats_for_account(user_id=uid)
    elif input_text.isdigit() and len(input_text) <= 2:
        player_data = get_playerdata_from_result_list(uid=uid, index=input_text)
        if 'errmsg' in player_data.keys():
            msg = player_data['errmsg']
            #await bot.send(ev, msg, at_sender=True)
            return msg
        membershipId = player_data['membershipId']
        membershipType = player_data['membershipType']
        stats_data = await get_pvp_general_historical_stats_for_account(user_id=uid, is_qqid=False, membershipId=membershipId, membershipType=membershipType)
    else:
        if is_steamid64(input_text):
                player_data = await search_player_from_steamID(input_text)
                player = player_data[0]
                membershipId = player['membershipId']
                membershipType = player['membershipType']
                stats_data = await get_pvp_general_historical_stats_for_account(user_id=uid, is_qqid=False, membershipId=membershipId, membershipType=membershipType)
        elif is_bungie_membershipid(input_text):
                stats_data = await get_pvp_general_historical_stats_for_account(user_id=uid, is_qqid=False, membershipId=input_text)
        else:
            stats_data = {"errmsg":f"玩家序号或ID输入错误，错误内容为【{input_text}】，请校验后重试"}
    if "errmsg" in stats_data.keys():
        msg = stats_data["errmsg"]
        return msg
        #await bot.send(ev, msg, at_sender=True)
    else:
        displayed_stats = ['activitiesEntered','hoursPlayed','killsDeathsRatio','efficiency','winRatio','kills','assists','deaths']
        displayName = stats_data['displayName']
        if no_name:
            msg = ""
        else:
            msg = f"[CQ:at,qq={uid}]\n{displayName}的PVP战绩："
        for stat_name in displayed_stats:
            try:
                stat_name_ts = stats_data[stat_name]['statIdTs']
                display_value = stats_data[stat_name]['displayValue']
                msg += f"\n{stat_name_ts}：{display_value}"
            except KeyError:
                pass
    return msg

async def d2_stat_trn_elo(user_id,arg:'',no_name=False):
    """
    返回固定格式ELO数据消息文本
    """
    season = str(await get_season_now())
    pattern_season = re.compile(r'#(\d{1,2})')
    pattern_identifier = re.compile(r'(7656\d{13}(\d{2})?)')
    if pattern_season.search(arg):
        season = pattern_season.search(arg).group(1)
        if not 0 < int(season) <= int(await get_season_now()):
            msg = f'啥b，现在才第{season}赛季'
            return msg
    if pattern_identifier.search(arg):
        identifier = pattern_identifier.search(arg).group(1)
        print(identifier)
        user_name =  await get_displayname(identifier, 1)
    elif '@' in arg:
        msg = f'哈批，输入的Steam64位ID或者BungieID错了，检查后再重试吧'
        return msg
    elif arg.isdigit() and len(arg) <= 2:
        player_data = get_playerdata_from_result_list(uid=user_id, index=arg)
        if 'errmsg' in player_data.keys():
            msg = player_data['errmsg']
            return msg
        identifier = player_data['membershipId']
        user_name =  await get_displayname(identifier, 0)
    else:
        config = load_player_link_data()
        if str(user_id) not in config:
            msg = "未绑定玩家信息, 请先通过【玩家搜索+昵称/Steam64位ID】来绑定玩家信息\n"
            return msg
        player_data = config[str(user_id)]
        identifier = player_data["membershipId"]
        user_name = player_data["displayName"]
    playlist_data = trn_playlist_search(identifier, season)
    for i in playlist_data:
        if type(i) == dict and 'errmsg' in i.keys():
            msg = i['errmsg']
            return msg
    if season != await get_season_now():
        if no_name:
            msg = []
        else:
            msg = [f'[CQ:at,qq={user_id}]\n{user_name}的第{season}赛季ELO查询结果：']
        for p in playlist_data:
            name = trn_playlist_nametrans(p['name'])
            rankname = trn_rank_nametrans(p['rankname'])
            msg.append(
                f"{name}：【{rankname}】{p['elo']}"
                )
        msg.append(f'\nELO数据来源：https://destinytracker.com/destiny-2/profile/steam/{identifier}/')
    else:
        if no_name:
            msg = []
        else:
            msg = [f'[CQ:at,qq={user_id}]\n{user_name}的ELO查询结果：']
        for p in playlist_data:
            try:
                per = 100 - float(p['percentile'])
                if str(per)[-1] != '0':
                    per = format(per,'.1f')
            except:
                per = 'None'
            name = trn_playlist_nametrans(p['name'])
            rankname = trn_rank_nametrans(p['rankname'])
            msg.append(
                f"{name}：【{rankname}】{p['elo']} #{p['rank']} {per}%"
                )
        msg.append(f'\n数据来源：https://destinytracker.com/destiny-2/profile/steam/{identifier}/')
    return '\n'.join(msg)