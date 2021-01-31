from . import *

tmp = {}

@sv.on_prefix(('玩家搜索','查询玩家'))
async def player_find(bot, ev):
    key = ev.user_id
    tmp[key] = {}
    name = ev.message.extract_plain_text()
    if not name:
        await bot.send(ev, '请输入要搜索的用户名或者Steam64位ID哦~')
        return
    ulist = playerSearch(name)
    if isinstance(ulist, dict) and 'err' in ulist.keys():
        msg = f'{ulist["err"]}'
        await bot.send(ev, msg, at_sender=True)
        return
    msg = ['请发送【绑定玩家+序号】绑定你的游戏账号~\n']
    for idx, player in enumerate(ulist):
            msg.append(
                f"{idx}.游戏平台：{player['platformSlug']}\n战绩页面 https://destinytracker.com/destiny-2/profile/steam/{player['platformUserIdentifier']}/"
            )
            tmp[key][str(idx)] = (player['platformUserIdentifier'], player['platformUserHandle'])
    msg.append('\n如果无法通过玩家昵称找到你的账号，可以直接使用Steam64位ID进行查询（也就是队伍加入码）')
    await bot.send(ev, '\n'.join(msg))

@sv.on_prefix(('绑定玩家'))
async def player_link(bot, ev):
    uid = ev.user_id
    if uid not in tmp:
        await bot.send(ev, '请先发送【玩家搜索+昵称/Steam64位ID】来搜索玩家哦')
        return
    idx = ev.message.extract_plain_text().strip()
    if not idx or not tmp[uid][idx]:
        identifier = tmp[uid]['0'][0]
        name = tmp[uid]['0'][1]
    else:
        identifier = tmp[uid][idx][0]
        name = tmp[uid][idx][1]
    code = linkPlayer(uid, name, identifier)
    if code != 0:
        msg = f'发生错误，请重试或联系维护人员'
        await bot.send(ev, msg, at_sender=True)
        return
    msg = f"绑定成功"
    await bot.send(ev, msg)

def playerSearch(text):
    user_list = []
    url = 'https://api.tracker.gg/api/v2/destiny-2/standard/search?platform=steam&query=' + text
    try:
        resp = requests.request('GET', url, timeout=5).json()
        for item in resp['data']:
            user_list.append(
                {
                    'platformId': item['platformId'],
                    'platformSlug': item['platformSlug'],
                    'platformUserIdentifier': item['platformUserIdentifier'],
                    'platformUserId': item['platformUserId'],
                    'platformUserHandle': item['platformUserHandle'],
                    'avatarUrl': item['platformUserIdentifier'],
                    'membershipType': item['additionalParameters']['membershipType'],
                    'membershipId': item['additionalParameters']['membershipId'],
                }
            )
        return user_list
    except Exception as e:
        logger.error(f'TRN玩家查询请求出错,错误信息为{e}')
        errmsg = {'err': f'玩家信息查询失败，错误信息为{e},请联系维护人员'}
        return errmsg

def loadConfig():
    if os.path.exists('/home/ubuntu/PurinBot/hoshino/modules/destiny2/tracker/player.json'):
        with open("/home/ubuntu/PurinBot/hoshino/modules/destiny2/tracker/player.json","r",encoding='utf-8') as dump_f:
            try:
                player_config = json.load(dump_f)
            except:
                player_config = {}
    else:
        player_config = {}
    return player_config

def saveConfig(config):
    with open("/home/ubuntu/PurinBot/hoshino/modules/destiny2/tracker/player.json","w",encoding='utf-8') as dump_f:
        json.dump(config,dump_f,indent=4,ensure_ascii=False)

def linkPlayer(user_id, user_name, identifier):
    player_config = loadConfig()
    player_info = {"user_id":user_id,"user_name":user_name,"identifier":identifier}
    player_config[str(user_id)] = player_info
    saveConfig(player_config)
    return 0