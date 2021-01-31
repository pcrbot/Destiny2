from . import *
from ..D2_API import *
from ..player_search import load_player_link_data, get_displayname
from .translate import *

async def get_chara_ids(user_id:str) -> list:
    config = load_player_link_data()
    try:
        player_data = config[str(user_id)] # 我是不看函数注释的傻逼
        profile_url = get_profile_url(membershipId=player_data['membershipId'], membershipType=player_data['membershipType'], components='100')
        resp = await destiny2_api_public(profile_url)
        chara_ids = resp.data['profile']['data']['characterIds']
        return chara_ids
    except KeyError as e:
        return

async def get_historical_stats_for_account(user_id:str='', groups=1, characters=0, is_user_local=True, **memberships):
    """
    获取指定玩家全角色历史数据
    :param user_id: QQ号
    :param groups:
                General:1   默认值 一般通过数据
                Weapons:2   枪械击杀数据
                Medals:3    奖牌数据
    :param characters: 
                    characters:0    单独返回每个character的stats 会标注deleted状态
                    mergedAllCharacters:1   返回包含已删除的所有character合并后的stats
                    mergedDeletedCharacters:2 返回所有已删除character合并后的stats
    :param is_user_local:
                    True: 使用本地储存的playerdata数据
                    False: 不使用本地数据
    :param **memberships:
                membershipType:str, membershipId:str
    :return:
            "results":{
                "allPvE":{
                },
                "allPvP":{
                }
            }
            "merged":{
                "allTime":{
                }
            }
                
    """
    config = load_player_link_data()
    if is_user_local:
        try:
            player_data = config[str(user_id)]
            membershipId = player_data['membershipId']
            membershipType = player_data['membershipType']
        except KeyError as e:
            hoshino.logger.error(f'd2-stat 无法在本地找到QQ号所对应玩家{e}')
            return
    else:
        try:
            membershipId = memberships['membershipId']
            membershipType = memberships['membershipType']
        except KeyError as e:
            hoshino.logger.error(f'd2-stat 玩家查询传参错误{memberships}')
            return
    try:
        url = get_historical_stats_for_account_url(membershipId=membershipId,membershipType=membershipType, groups=groups)
        resp = await destiny2_api_public(url)
        if characters == 0:
            stats_data = resp.data['characters']
        elif characters == 1:
            stats_data = resp.data['mergedAllCharacters']
        elif characters == 2:
            stats_data = resp.data['mergedDeletedCharacters']
        else:
            raise Exception
        return stats_data
    except Exception as e:
        return

def ts_stat_name(stat_name:str):
    """
    翻译stat项目名
    """
    try:
        stat_name_zh = ts[stat_name]
        return stat_name_zh
    except KeyError:
        return stat_name

async def get_pvp_general_historical_stats_for_account(user_id:str, is_qqid=True, membershipId='', membershipType=3) -> dict:
    """
    返回经过处理的账号所有角色的pvp_general数据
    :param: is_qqid: 为True的话则视为QQ号, 为False的话则视为d2的membershipId
    :return:
            "statId": {
                "value": float,
                "displayValue": str,
                "statIdTs": str
            }
    """
    if is_qqid:
        stats_data = await get_historical_stats_for_account(user_id=user_id, groups=1, characters=1)
    else:
        stats_data = await get_historical_stats_for_account(groups=1, characters=1, is_user_local=False, membershipId=membershipId, membershipType=membershipType)
    try:
        pvp_stats = stats_data['results']['allPvP']['allTime']
    except KeyError as e:
        errmsg = f'玩家历史战绩查询失败，错误原因是{e}'
        return {"errmsg":errmsg}
    pga = {}
    basic = {}
    for stat_name in pvp_stats:
        data = pvp_stats[stat_name]
        if 'pga' in data.keys():
            new_name = f'{stat_name}_pga'
            pga[new_name] = data['pga']
            data.pop('pga')   
        basic[stat_name] = data['basic']
    basic.update(pga)
    total_stats = basic.copy()
    # 新增胜率
    win_count = total_stats['activitiesWon']['value']
    total_act_count = total_stats['activitiesEntered']['value']
    total_stats['winRatio'] = get_winRatio(win_count, total_act_count) 
    # 新增游玩时长(小时)
    seconds_count = total_stats['secondsPlayed']['value']
    total_stats['hoursPlayed'] = get_hoursPlayed(seconds_count)
    # 本地化
    for stat_name in total_stats:
        data = total_stats[stat_name]
        data['statIdTs'] = ts_stat_name(stat_name)
    # 新增玩家名
    if not is_qqid:
        displayName = await get_displayname(membershipId)
    else:
        displayName = await get_displayname(user_id, uid_type=1)
    total_stats['displayName'] = displayName
    return total_stats

def get_winRatio(win_count, total_act_count) -> dict:
    winRatio = (win_count / total_act_count)*100
    wr_str = str(winRatio)
    if wr_str.rindex(".") < 4:
        wr_str += "00"
    wr_index = wr_str.index(".")
    displayValue = f"{str(winRatio)[:wr_index + 2]}%"
    return {"value":winRatio, "displayValue":displayValue}

def get_hoursPlayed(seconds) -> str:
    hoursPlayed = seconds / 3600
    displayValue = str(round(hoursPlayed, 1))
    return {"value":hoursPlayed, "displayValue":displayValue + "h"}
    