from .D2_API import *
from .steamid_converter import is_steamid64, is_bungie_membershipid

player_list_tmp = {} # 全局储存玩家搜索结果的 最好做一下持久化

def get_playerdata_from_result_list(uid:str, index:str):
    try:
        player_data = {}
        data_summary = player_list_tmp[str(uid)] # 嗯没错 我是傻逼*2
        player_data = data_summary[index]
    except KeyError as e:
        reason = str(e)[1:-1] # 转成str 去除首尾'号
        if reason == uid or not player_list_tmp:
            errmsg = f'你个憨批，目前还没用过玩家搜索，请先使用【d2搜索玩家 昵称】进行玩家搜索'
        elif reason == index:
            errmsg = f'変態不審者さん、查询时请输入正确的玩家搜索结果序号...你输入的序号“{index}”是错的啦！'
        else:
            errmsg = f'玩家搜索结果查询出错...原因是{traceback.format_exc()}' # 如果不是自用的话建议把完整输出改成e
        player_data['errmsg'] = errmsg
    return player_data

async def player_search(inputText):
    if is_steamid64(inputText):
        player_list = await search_player_from_steamID(inputText)
        if not player_list:
            player_list = await search_player_from_user_name(inputText)
    else:
        player_list = await search_player_from_user_name(inputText)
    return player_list


async def search_player_from_steamID(SteamId):
    """
    通过Steam64位ID搜索玩家
    :return:
    membershipType
    membershipId
    displayName
    """
    url = get_membership_from_hard_linked_credential_url(SteamId)
    resp = await destiny2_api_public(url)
    membershipId = resp.data['membershipId']
    membershipType = resp.data['membershipType']
    displayName = await get_displayname(membershipId)
    player_data = {}
    player_data['membershipType'] = membershipType
    player_data['membershipId'] = membershipId
    player_data['displayName'] = displayName
    return [player_data]

# 通过用户名搜索各平台的玩家
# 'membershipType'
# 'membershipId'
# 'displayName'

async def search_player_from_user_name(inputText):
    """
    通过用户名搜索各平台的玩家
    :return:
    'membershipType'
    'membershipId'
    'displayName'
    """
    player_data = []
    for i in range(3):
        membershipType = str(3 - i)
        url = search_destiny_player_url(inputText, membershipType)
        resp = await destiny2_api_public(url)
        for i in resp.data:
            tmp = {}
            tmp['membershipType'] = i['membershipType']
            tmp['membershipId'] = i['membershipId']
            tmp['displayName'] = i['displayName']
            player_data.append(tmp)
    return player_data

async def get_displayname(uid, uid_type=0):
    """
    :param uid_type: 
        0: membershipId
        1: qq_uid
        2: steamid64
    """
    try:
        if uid_type == 1:
            cfg = load_player_link_data()
            uid = cfg[str(uid)]['membershipId']
        membership_url = get_memberships_by_id_url(uid)
        resp = await destiny2_api_public(membership_url)
        displayName = resp.data["destinyMemberships"][0]["displayName"]
        return displayName
    except Exception as e:
        if uid_type == 1:
            cfg = load_player_link_data()
            if str(uid) in cfg.keys() and "displayName" in cfg[str(uid)].keys():
                return cfg[str(uid)]["displayName"]
            else:
                return None
        else:
            return None

def load_player_link_data():
    if os.path.exists('/home/ubuntu/PurinBot/hoshino/modules/destiny2/playerdata.json'):
        with open("/home/ubuntu/PurinBot/hoshino/modules/destiny2/playerdata.json","r",encoding='utf-8') as dump_f:
            try:
                player_config = json.load(dump_f)
            except:
                player_config = {}
    else:
        player_config = {}
    return player_config

def save_player_link_data(data):
    with open("/home/ubuntu/PurinBot/hoshino/modules/destiny2/playerdata.json","w",encoding='utf-8') as dump_f:
        json.dump(data,dump_f,indent=4,ensure_ascii=False)

def link_player(QQ_NUM, player_data):
    origin_data = load_player_link_data()
    origin_data[str(QQ_NUM)] = player_data
    save_player_link_data(origin_data)