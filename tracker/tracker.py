from . import *
from .translate import *

@sv.on_prefix(('elo查询','elo')) #赛季ELO分数查询
async def elo_search(bot, ev):
    season = str(getSeasonNow())
    user_id = ev.user_id
    arg = ev.message.extract_plain_text().strip()
    patternSeason = re.compile(r'#(\d{1,2})')
    patternIdentifier = re.compile(r'@(\d{17}(\d{2})?)')
    if patternSeason.search(arg):
        season = patternSeason.search(arg).group(1)
        if not 0 < int(season) <= int(getSeasonNow()):
            await bot.send(ev, f'啥b，现在才第{getSeasonNow()}赛季', at_sender=True)
            return
    if patternIdentifier.search(arg):
        identifier = patternIdentifier.search(arg).group(1)
        user_name = await errSend(bot, ev, identifierToName(identifier))
    elif '@' in arg:
        await bot.send(ev, f'哈批，输入的Steam64位ID或者BungieID错了，检查后再重试吧', at_sender=True)
        return
    else:
        config = loadConfig()
        if str(user_id) not in config:
            msg = "未绑定玩家信息, 请先通过【玩家搜索+昵称/Steam64位ID】来绑定玩家信息\n"
            await bot.send(ev, msg, at_sender=True)
            return
        playerData = config[str(user_id)]
        identifier = playerData["identifier"]
        user_name = playerData["user_name"]
    data = await errSend(bot, ev, playlistSearch(identifier, season))
    if not user_name:
        return
    if season != getSeasonNow():
        msg = [f'\n{user_name}的第{season}赛季ELO查询结果：']
        for p in data:
            name = playListNameTrans(p['name'])
            rankname = rankNameTrans(p['rankname'])
            msg.append(
                f"{name}：【{rankname}】{p['elo']}"
                )
        msg.append(f'\n数据来源：https://destinytracker.com/destiny-2/profile/steam/{identifier}/')
    else:
        msg = [f'\n{user_name}的ELO查询结果：']
        for p in data:
            try:
                per = 100 - float(p['percentile'])
                if str(per)[-1] != '0':
                    per = format(per,'.1f')
            except:
                per = 'None'
            name = playListNameTrans(p['name'])
            rankname = rankNameTrans(p['rankname'])
            msg.append(
                f"{name}：【{rankname}】{p['elo']} #{p['rank']} {per}%"
                )
        msg.append(f'\n数据来源：https://destinytracker.com/destiny-2/profile/steam/{identifier}/')
    await bot.send(ev, '\n'.join(msg), at_sender=True)

    
def playlistSearch(identifier, season):
    playlist = []
    url = 'https://api.tracker.gg/api/v2/destiny-2/standard/profile/steam/' + identifier + '/segments/playlist?season=' + season
    try:
        resp = requests.request('GET', url, timeout=5).json()
        for item in resp['data']:
            playlist.append(
                {
                    'group': item['attributes']['group'], #分类(qp或者comp)
                    'name': item['metadata']['name'], #模式名称
                    'rank': item['stats']['elo']['rank'], #世界排名
                    'rankname': item['stats']['elo']['metadata']['rankName'], #段位名称 中文转换！！！！！！！
                    'elo': item['stats']['elo']['value'], #ELO分数
                    'percentile': item['stats']['elo']['percentile'], #世界排名百分比(从100开始算)
                    'wins': item['stats']['activitiesWon']['value'], #获胜次数
                    'wl': item['stats']['wl']['displayValue'], #百分比胜率(精确到1位小数)
                    'kd': item['stats']['kd']['displayValue'], #KD(精确到2位小数)
                    'kad': item['stats']['kad']['displayValue'], #KAD(精确到2位小数)
                    'kda': item['stats']['kda']['displayValue'], #KDA(精确到2位小数)
                    'assists': item['stats']['assists']['displayValue'], #助攻
                    'kpg': item['stats']['killsPga']['displayValue'], # Kill per Game(精确到2位小数)
                }
            )
        return playlist
    except Exception as e:
        logger.error(f'TRN数据查询请求出错,错误信息为{e}')
        errmsg = {'err': f'玩家数据查询失败，错误信息为{e},请检查后重试或联系维护人员'}
        return errmsg

async def errSend(bot, ev, data):
    if isinstance(data, dict) and 'err' in data.keys(): #错误捕获
        msg = f'{data["err"]}'
        await bot.send(ev, msg, at_sender=True)
        return
    else:
        return(data)

def playListNameTrans(nameEN):
    if nameEN not in playListNameEN2CHS:
        return nameEN
    nameCHS = playListNameEN2CHS[f'{nameEN}']
    return nameCHS

def rankNameTrans(nameEN):
    if nameEN not in rankNameEN2CHS:
        return nameEN
    nameCHS = rankNameEN2CHS[f'{nameEN}']
    return nameCHS

def getSeasonNow():
    season12Time = datetime.fromtimestamp(1605110400)
    if datetime.now() < season12Time:
        season = '11'
    else:
        season = '12'
    return season

def identifierToName(identifier):
    try:
        user_list = playerSearch(identifier)
        name = user_list[0]['platformUserHandle']
        return name
    except Exception as e:
        logger.error(f'TRN数据查询请求出错,错误信息为{e}')
        errmsg = {'err': f'玩家数据查询失败，错误信息为{e},请检查后重试或联系维护人员'}
        return errmsg