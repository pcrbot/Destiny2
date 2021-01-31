from .D2_API import *
import re
import math
import requests
import cloudscraper
from bs4 import BeautifulSoup
from hoshino import aiorequests


key = 'FCE99B5298E8A0BFCA100ADF1E5FFD3D'

async def merge_steam_details(steamid):
    try:
        steam_ids = await get_steamids(steamid)
        steamID64 = steam_ids['steamID64']
        steamID3 = steam_ids['steamID3']
        steamID = steam_ids['steamID']
        steam_summary = await get_steam_user_summary(steamID64)
        if 'lastlogoff' not in steam_summary.keys(): # steam返回值有可能没有lastlogoff 很啥b
            lastlogoff = 'None'
        else:
            lastlogoff = datetime.datetime.fromtimestamp(steam_summary['lastlogoff'])
        personaname = steam_summary['personaname']
        avatar_url = steam_summary['avatarfull']
        timecreated = datetime.datetime.fromtimestamp(steam_summary['timecreated'])
        profileurl = f'https://steamcommunity.com/profiles/{steamID64}'
        msg = f'''
User Name：{personaname}
SteamID64：{steamID64}
SteamID：{steamID}
SteamID3：{steamID3}
Last Logoff：{lastlogoff}
Time Created：{timecreated}
Profile Page: {profileurl}
[CQ:image,file={avatar_url}]
'''
    except ValueError as e:
        msg = f'转换失败...错误原因为：{e}'
    except KeyError:
        pass
    return msg

async def get_steamid_from_username(user_name,is_d2_msid=False):
    """
    通过棒鸡官网进行查询 没有公开API 啥时候会失效俺也不知道
    但是算是独家工具惹
    虽然局限于steam平台的命运2玩家qwq
    todo: 重名时需要增加选择
    """
    try:
        if not is_d2_msid:
            url = search_destiny_player_url(displayName=user_name, membershipType=3)
            d2_resp = await destiny2_api_public(url)
            d2_data = d2_resp.data
            membershipId = d2_data[0]['membershipId']
        else:
            membershipId = user_name
        msd_resp = await destiny2_api_public(get_memberships_by_id_url(membershipId=membershipId,membershipType=3)) # 通过d2的membershipId获取BungieNet的ID
        msd_data = msd_resp.data
        bungie_id = msd_data['bungieNetUser']['membershipId']
        bungie_profie_url = f'https://www.bungie.net/zh-cht/Profile/{bungie_id}'
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(bungie_profie_url, timeout=5, proxies=PROXIES).text
        soup = BeautifulSoup(resp, 'lxml')
        div_results = soup.find_all('div', class_="title")
        for i in div_results:
            data = i.text
            if '(ID: 7656' in data:
                steamid = data[-18:-1]
                if is_steamid64(steamid):
                    return steamid
                else:
                    pass
    except Exception as e:
        hoshino.logger.error(f'GetSteamIdFromUsername error, reason: {e}')
        return None

def get_input_type(input_text):
    if input_text.isdigit and len(input_text) == 17 and input_text[:4] == '7656':
        input_text_type = 'steamid64'
    elif len(input_text) == 19 and input_text[:8] == 'STEAM_0:':
        input_text_type = 'steamid'
    elif len(input_text) == 15 and input_text[:5] == '[U:1:' and input_text[-1] == ']':
        input_text_type = 'steamid3'
    elif input_text.isalnum():
        input_text_type = 'vanityurl'
    else:
        raise ValueError(f"Input type error: {input_text}")
    return input_text_type

async def get_steamids(input_text):
    input_text_type = get_input_type(input_text)
    if input_text_type == 'vanityurl':
        steamID64 = await vanityurl_to_steamID64(input_text)
        steamID = to_steamID(steamID64)
        steamID3 = to_steamID3(steamID64)
    elif input_text_type == 'steamid64':
        steamID = to_steamID(input_text)
        steamID3 = to_steamID3(input_text)
        steamID64 = input_text
    elif input_text_type == 'steamid3':
        steamID64 = to_steamID64(input_text)
        steamID = to_steamID(input_text)
        steamID3 = input_text
    elif input_text_type == 'steamid':
        steamID64 = to_steamID64(input_text)
        steamID3 = to_steamID3(input_text)
        steamID = input_text
    else:
        raise ValueError(f"Type error: {input_text}")
    return {'steamID':steamID, 'steamID3':steamID3, 'steamID64':steamID64}

async def get_steam_user_summary(steamID64):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={key}&steamids={steamID64}'
    resp = await aiorequests.get(url, headers = HEADERS, proxies=PROXIES, timeout=5)
    resp = await resp.json()
    if resp['response']['players']:
        return resp['response']['players'][0]
    else:
        raise ValueError(f"No match: {steamID64}")

async def vanityurl_to_steamID64(vanityurl:str):
    url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={key}&vanityurl={vanityurl}'
    resp = await aiorequests.get(url, headers = HEADERS, proxies=PROXIES, timeout=5)
    resp = await resp.json()
    if resp['response']['success'] == 1:
        return resp['response']['steamid']
    else:
        raise ValueError(f"No match: {vanityurl}")

def is_steamid64(input_text:str):
    if input_text.isdigit() and len(input_text) == 17 and input_text[:4] == '7656':
        return True
    else:
        return False

def is_bungie_membershipid(input_text:str):
    if input_text.isdigit() and len(input_text) == 19 and input_text[:4] == '4611':
        return True
    else:
        return False

def to_steamID(steamID):
    """
    Convert to steamID

    A steamID is unique to each steam account, 
    Formatted with digits as x "STEAM_0:x:xxxxxxxx"

    Parameters
    ----------
    steamID : int or str
        steamID3 or steamID64 to convert to steamID

    Returns
    -------
    str
        steamID value

    """

    id_str = str(steamID)

    if re.search("^STEAM_", id_str): # Already a steamID
        return id_str

    elif re.search("^\[.*\]$", id_str): # If passed steamID3

        id_split = id_str.split(":") # Split string into 'Universe', Account type, and Account number
        account_id3 = int(id_split[2][:-1]) # Remove ] from end of steamID3

        if account_id3 % 2 == 0:
            account_type = 0
        else:
            account_type = 1

        account_id = (account_id3 - account_type) // 2

    elif id_str.isnumeric(): # Passed steamID64

        check_steamID64_length(id_str) # Validate id passed in

        id64_base = 76561197960265728 # steamID64 are all offset from this value
        offset_id = int(id_str) - id64_base

        # Get the account type and id
        if offset_id % 2 == 0:
            account_type = 0
        else:
            account_type = 1

        account_id = ((offset_id - account_type) // 2)

    return "STEAM_0:" + str(account_type) + ":" + str(account_id)

def to_steamID3(steamID):
    """
    Convert to steamID3

    A steamID3 is unique to each steam account, 
    Formatted with digits as x "[U:1:xxxxxxxx]"

    Parameters
    ----------
    steamID : int or str
        steamID or steamID64 to convert to steamID3

    Returns
    -------
    str
        steamID3 value

    """

    id_str = str(steamID)

    if re.search("^\[.*\]$", id_str): # Already a steamID3
        return id_str

    elif re.search("^STEAM_", id_str): # If passed steamID

        id_split = id_str.split(":") # Split string into 'Universe', Account type, and Account number

        account_type = int(id_split[1]) # Check for account type
        account_id = int(id_split[2]) # Account number, needs to be doubled when added to id3

        # Join together in steamID3 format
        return "[U:1:" + str(((account_id + account_type) * 2) - account_type) + "]"

    elif id_str.isnumeric(): # Passed steamID64
        
        check_steamID64_length(id_str) # Validate id passed in

        id64_base = 76561197960265728 # steamID64 are all offset from this value
        offset_id = int(id_str) - id64_base

        # Get the account type and id
        if offset_id % 2 == 0:
            account_type = 0
        else:
            account_type = 1

        account_id = ((offset_id - account_type) // 2) + account_type

        # Join together in steamID3 format
        return "[U:1:" + str((account_id * 2) - account_type) + "]"
        
    else:
        raise ValueError(f"Unable to decode steamID: {steamID}")


def to_steamID64(steamID, as_int = False):
    """
    Convert to steamID64

    A steamID64 is a 17 digit number, unique to each steam account

    Parameters
    ----------
    steamID : int or str
        steamID or steamID3 to convert to steamID64
    as_int : bool
        If the steamID64 is returned as an integer rather than string, Default = False

    Returns
    -------
    int or str
        steamID64 value

    """

    id_str = str(steamID)
    id_split = id_str.split(":") # Split string into 'Universe', Account type, and Account number
    id64_base = 76561197960265728 # steamID64 are all offset from this value

    if id_str.isnumeric(): # Already a steamID64

        check_steamID64_length(id_str) # Validate id passed in
        if as_int:
            return id64
        else:
            return str(id64)

    elif re.search("^STEAM_", id_str): # If passed steamID
        
        account_type = int(id_split[1]) # Check for account type
        account_id = int(id_split[2]) # Account number, needs to be doubled when added to id64

    elif re.search("^\[.*\]$", id_str): # If passed steamID3

        account_id3 = int(id_split[2][:-1]) # Remove ] from end of steamID3

        if account_id3 % 2 == 0:
            account_type = 0
        else:
            account_type = 1

        account_id = (account_id3 - account_type) // 2

    else:
        raise ValueError(f"Unable to decode steamID: {steamID}")


    id64 = id64_base + (account_id * 2) + account_type

    # Check if returning as string or integer
    if as_int:
        return id64
    else:
        return str(id64)


def check_steamID64_length(id_str :str):
    """
    Check if a steamID64 is of the correct length, raises ValueError if not.

    Not really for you to use

    Parameters
    ----------
    id_str : str
        steamID64 to check length of

    """

    if len(id_str) != 17:
        raise ValueError(f"Incorrect length for steamID64: {id_str}")

