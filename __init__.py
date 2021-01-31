from .D2_Manifest import *
from .player_search import *
from .steamid_converter import *

import hoshino
from hoshino import Service, logger
from aiocqhttp.exceptions import ActionFailed

sv = Service('d2-main')
config = hoshino.config.destiny2.destiny2_config
day = f'1/{config.MANIFEST_AUTO_UPDATE_DAY}'
hour = str(config.MANIFEST_AUTO_UPDATE_HOUR)
minute = str(config.MANIFEST_AUTO_UPDATE_MINUTE)

@sv.on_fullmatch(('d2fixmani'))
async def d2_fix_manifest(bot, ev):
    await update_manifest(language=LOAD_LANGUAGES)
    
from .D2_API import *

@sv.on_fullmatch(('更新Mani','更新Manifest','更新mani','更新manifest'))
async def update_mani(bot,ev):
    await bot.send(ev, '正在更新Manifest文件...')
    await update_manifest()
    await bot.send(ev, 'Manifest文件已更新完毕')

@sv.scheduled_job('cron', day=day, hour=hour, minute=minute)
async def auto_update_mani():
    await update_manifest()
    hoshino.logger.info('已自动更新Manifest文件')

@sv.on_prefix(('d2搜索玩家','d2玩家搜索'))
async def d2_player_search(bot, ev):
    key = str(ev.user_id)
    player_list_tmp[key] = {}
    name = ev.message.extract_plain_text()
    try:
        resp = await player_search(name)
        msg = ['请发送【d2绑定玩家+序号】绑定你的游戏账号~\n序号为0可以省略哦\n']
        for idx, item in enumerate(resp):
            membershipType = item['membershipType']
            platform = membershiptype_converter(membershipType)
            membershipId = item['membershipId']
            displayName = item['displayName']
            steamid = await get_steamid_from_username(user_name=membershipId, is_d2_msid=True)
            msg.append(
                    f"{idx}.用户名：{displayName}\n游戏平台：{platform}\nSteamID64：{steamid}\n"
                )
            player_list_tmp[key][str(idx)] = {"membershipType":membershipType, "membershipId":membershipId, "displayName":displayName, "steamId64":steamid}
        msg.append('如果无法通过玩家昵称找到你的账号，可以直接发送【d2绑定steam Steam64位ID】（也就是队伍加入码）')
        await bot.send(ev, '\n'.join(msg))
    except Exception as e:
        hoshino.logger.error(e)
        await bot.send(ev, f'搜索玩家出错，错误信息为\n{e}')
        
@sv.on_prefix(('d2绑定玩家','d2玩家绑定'))
async def d2_player_link(bot, ev):
    uid = str(ev.user_id)
    idx = ev.message.extract_plain_text().strip()
    if uid not in player_list_tmp:
        await bot.send(ev, '请先发送【d2玩家搜索+昵称】来搜索玩家哦')
        return
    if not idx or not player_list_tmp[uid][idx]:
        player_data = player_list_tmp[uid]['0']
    else:
        player_data = player_list_tmp[uid][idx]
    link_player(uid, player_data)
    await bot.send(ev, '已成功绑定玩家信息~', at_sender=True)

@sv.on_fullmatch(('d2查看绑定','d2绑定查看'))
async def d2_player_link_detail(bot, ev):
    uid = ev.user_id
    try:
        data = load_player_link_data()
        user_data = data[str(uid)]
        displayName = user_data['displayName']
        membershipType = user_data['membershipType']
        platform = membershiptype_converter(membershipType)
        membershipId = user_data['membershipId']
        msg = f'目前绑定的Destiny2玩家信息如下\n用户名：{displayName}\n游戏平台：{platform}\n玩家ID：{membershipId}'
        await bot.send(ev, msg, at_sender=True)
    except KeyError:
        await bot.send(ev, '暂无绑定玩家信息哦，可以发送【d2绑定帮助】查看绑定帮助~')

@sv.on_prefix(('d2绑定steam','d2steam绑定'))
async def d2_steam_player_link(bot, ev):
    uid = ev.user_id
    steamid = ev.message.extract_plain_text().strip()
    if is_steamid64(steamid):
        r = await search_player_from_steamID(steamid)
        player_data = r[0]
        player_data['steamId64'] = steamid
        link_player(uid, player_data)
        await bot.send(ev, f"已成功绑定玩家信息，用户名为{player_data['displayName']}")
    else:
        await bot.send(ev, '请输入正确的Steam64位ID，可以在游戏内发送【/id】获取', at_sender=True)

@sv.on_prefix(('steamid查询'))
async def steamid_finder(bot, ev):
    uid = ev.user_id
    input_text = ev.message.extract_plain_text().strip()
    if not input_text:
        player_data = get_playerdata_from_result_list(uid=uid, index=0)
        if 'errmsg' in player_data.keys():
            msg = player_data['errmsg']
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            steamid = player_data['steamId64']
    elif input_text.isdigit() and len(input_text) <= 2:
        player_data = get_playerdata_from_result_list(uid=uid, index=input_text)
        if 'errmsg' in player_data.keys():
            msg = player_data['errmsg']
            await bot.send(ev, msg, at_sender=True)
            return
        else:
            steamid = player_data['steamId64']
    else:
        steamid = input_text
    msg = await merge_steam_details(steamid)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix(('steam玩家搜索','steam用户搜索','steam昵称搜索','steam玩家查询','steam搜索玩家'))
async def steamun_finder(bot, ev):
    user_name = ev.message.extract_plain_text().strip()
    if is_bungie_membershipid(user_name):
        steamid = await get_steamid_from_username(user_name=user_name,is_d2_msid=True)
    else:
        steamid = await get_steamid_from_username(user_name=user_name)
    if not steamid:
        msg = f'未查询到昵称为{user_name}的玩家'
        await bot.send(ev, msg)
        return
    msg = await merge_steam_details(steamid)
    await bot.send(ev, msg, at_sender=True)

@sv.on_prefix('d2test')
async def d2test(bot, ev):
    pass

@sv.on_prefix('d2search')
async def d2sh(bot, ev):
    name = ev.message.extract_plain_text().strip()
    try:
        item_hash = ITEM_DICT[name]
        await bot.send(ev, str(item_hash))
    except KeyError:
        await bot.send(ev, f'没找到【{name}】哦~')