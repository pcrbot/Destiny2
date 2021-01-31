#import grequests
#from gevent import monkey
import requests, json, os, sqlite3
from hoshino import aiorequests
from .D2_Manifest import *

ROOT = 'https://www.bungie.net/Platform'

MANIFEST = {}
ITEM_DICT = {}
for lang in LOAD_LANGUAGES:
    MANIFEST[lang] = init_manifest(lang)
    mani = MANIFEST[lang]['DestinyInventoryItemDefinition']
    for item in mani:
        try:
            name = mani[item]["displayProperties"]["name"]
            ITEM_DICT[name] = item
        except KeyError:
            pass

def get_destiny_entity_definition(entityType, entityHash, language=DEFAULT_LANGUAGE):
    entity_data = MANIFEST[language][entityType][entityHash]
    return entity_data

async def destiny2_api_public(url):
    response = await aiorequests.get(url, headers = HEADERS, proxies=PROXIES, timeout=5)
    response_status = response.status_code
    response_url = response.url
    if response_status == 200:
        result = await response.json()
    else:
        result = None
    return ResponseSummary(response_status, response_url, result)

class ResponseSummary:
    def __init__(self, status, url, result=None):
        self.status = status
        self.url = url
        self.data = None
        self.message = None
        self.error_code = None
        self.error_status = None
        self.exception = None
        if self.status == 200:
            self.message = result['Message']
            self.error_code = result['ErrorCode']
            self.error_status = result['ErrorStatus']
            if self.error_code == 1:
                try: 
                    self.data = result['Response']
                except Exception as e:
                    hoshino.logger.error("ResponseSummary: 200 status and error_code 1, but there was no result['Response']")
                    hoshino.logger.error("Exception: {0}.\nType: {1}".format(e, e.__class__.__name__))
                    self.exception = e.__class__.__name__
            else:
                hoshino.logger.error('No data returned for url: {0}.\n {1} was the error code with status 200.'.format(self.url, self.error_code))
        else:
            hoshino.logger.error('Request failed for url: {0}.\n.Status: {1}'.format(self.url, self.status))
  
    def __repr__(self):
        """What will be displayed/printed for the class instance."""
        disp_header =       "<" + self.__class__.__name__ + " instance>\n"
        disp_data =         ".data: " + str(self.data) + "\n"
        disp_url =          ".url: " + str(self.url) + "\n"
        disp_message =      ".message: " + str(self.message) + "\n"
        disp_status =       ".status: " + str(self.status) + "\n"
        disp_error_code =   ".error_code: " + str(self.error_code) + "\n"
        disp_error_status = ".error_status: " + str(self.error_status) + "\n"
        disp_exception =    ".exception: " + str(self.exception)
        return disp_header + disp_data + disp_url + disp_message + \
               disp_status + disp_error_code + disp_error_status + disp_exception

def membershiptype_converter(membershipType):
    membershiptypes = {1:'Xbox', 2:'Psn', 3:'Steam', 4:'Blizzard', 5:'Stadia'}
    try:
        converted_name = membershiptypes[membershipType]
        return converted_name
    except KeyError:
        return 'UnKnow'

def search_destiny_player_url(displayName, membershipType):
    url = ROOT + f'/Destiny2/SearchDestinyPlayer/{membershipType}/{displayName}'
    return url

def get_membership_from_hard_linked_credential_url(credential, crType='SteamId'):
    url = ROOT + f'/User/GetMembershipFromHardLinkedCredential/{crType}/{credential}'
    return url

def get_memberships_by_id_url(membershipId, membershipType=-1):
    url = ROOT + f'/User/GetMembershipsById/{membershipId}/{membershipType}'
    return url

def get_profile_url(membershipId, membershipType, **query_params):
    """ query_params
    components[array]:
        Profiles: 100
        ProfileInventories: 102
        ProfileCurrencies: 103
        ProfileProgression: 104
        PlatformSilver: 105
    """
    url = ROOT + f'/Destiny2/{membershipType}/Profile/{membershipId}/'
    if query_params:
        url += '?'
        for i in query_params:
            url += (f'{i}={query_params[i]}&')
        url = url[:-1]
    return url    

def get_character_url(membershipType, membershipId, characterId, **query_params):
    """ query_params
    components[array]:
        Characters: 200 
        CharacterProgressions: 201
        CharacterRenderData: 203
        CharacterActivities: 204
        CharacterEquipment: 205
    """
    url = ROOT + f'/Destiny2/{membershipType}/Profile/{membershipId}/Character/{characterId}/'
    if query_params:
        url += '?'
        for i in query_params:
            url += (f'{i}={query_params[i]}&')
        url = url[:-1]
    return url

def get_common_settings_url(language=DEFAULT_LANGUAGE):
    url = ROOT + f'/Settings?lc={language}'
    return url

def get_destiny_entity_definition_url(entityType, hashIdentifier, language=DEFAULT_LANGUAGE, value=''):
    url = ROOT + f'/Destiny2/Manifest/{entityType}/{hashIdentifier}?lc={language}'
    if not value:
        return url
    else:
        return url + f'&value={value}'
        
def get_public_vendors_url(**query_params):
    """ query_params
    components[array]:
        VendorSales: 402 
        VendorCategories: 401
        Vendors: 400 
    """
    url = ROOT + f'/Destiny2/Vendors/'
    if query_params:
        url += '?'
        for i in query_params:
            url += (f'{i}={query_params[i]}&')
        url = url[:-1]
    return url

def get_historical_stats_url(membershipType, membershipId, characterId, **query_params):
    """query_params
    dayend, daystart, groups, modes, periodType
    dayend, daystart[str]: 
        YYYY-MM-DD UTC 31days longest
    groups[array]: 
        General:1, Weapons:2, Medals:3
    """
    url = ROOT + f'/Destiny2/{membershipType}/Account/{membershipId}/Character/{characterId}/Stats/'
    if query_params:
        url += '?'
        for i in query_params:
            url += (f'{i}={query_params[i]}&')
        url = url[:-1]
    return url

def get_historical_stats_for_account_url(membershipType, membershipId, **query_params):
    """query_params
    groups[array]: 
        General:1, Weapons:2, Medals:3
    """
    url = ROOT + f'/Destiny2/{membershipType}/Account/{membershipId}/Stats/'
    if query_params:
        url += '?'
        for i in query_params:
            url += (f'{i}={query_params[i]}&')
        url = url[:-1]
    return url

async def get_current_season_detail(language=DEFAULT_LANGUAGE):
    common_settings = await destiny2_api_public(get_common_settings_url(language=language))
    current_season_hash = common_settings.data['destiny2CoreSettings']['currentSeasonHash']
    season_detail = get_destiny_entity_definition(entityType='DestinySeasonDefinition', entityHash=current_season_hash, language=language)
    return season_detail

async def get_xur_sale_items(language=DEFAULT_LANGUAGE):
    xur_sales_item_summary = {}
    xur_sales_url = get_public_vendors_url(components='402')
    xur_sales_summary = await destiny2_api_public(xur_sales_url)
    xur_sales_summary = xur_sales_summary.data['sales']['data']['2190858386']['saleItems']
    for item in xur_sales_summary:
        item_data = xur_sales_summary[item]
        item_hash = item_data['itemHash']
        try:
            item_data = extract_item_detail(item_hash, language)
            if item_data:
                item_data = json.loads(item_data)
                xur_sales_item_summary[item_hash] = item_data
        except KeyError:
            hoshino.logger.exception(f"Item {item_hash} not find")
            continue
    
    json_data = json.dumps(xur_sales_item_summary)
    return json_data

def extract_item_detail(item_hash, language=DEFAULT_LANGUAGE):
    item_category_dict = {}
    item_perks = {}
    item_summary = get_destiny_entity_definition('DestinyInventoryItemDefinition', item_hash, language)
    if item_summary['itemType'] in [2,3]:
        item_name = item_summary['displayProperties']['name']
        #item_type_and_tier = item_summary['itemTypeAndTierDisplayName']
        item_type = item_summary['itemTypeDisplayName']
        item_damage_type = None
        if item_summary['defaultDamageType']:
            item_damage_type_summary = get_destiny_entity_definition('DestinyDamageTypeDefinition', item_summary['defaultDamageTypeHash'], language)
            item_damage_type = item_damage_type_summary['displayProperties']['name']
        item_description = item_summary['displayProperties']['description']
        item_icon = None
        if item_summary['displayProperties']['hasIcon']:
            item_icon = 'https://www.bungie.net' + item_summary['displayProperties']['icon']
        item_tier_type = item_summary['inventory']['tierTypeName']
        item_categories = item_summary['itemCategoryHashes']
        for category_hash in item_categories:
            category_summary = get_destiny_entity_definition('DestinyItemCategoryDefinition', category_hash, language)
            if not category_summary['groupCategoryOnly']:
                category_hash = category_summary['hash']
                item_category_dict[category_hash] = category_summary['displayProperties']['name']
                if category_hash == 22 and language == 'zh-cht':
                    item_category_dict[category_hash] =  "泰坦" # 傻逼棒鸡外包翻译错误
            else:
                item_root_category = {category_summary['hash']: category_summary['displayProperties']['name']}
        
        item_stats = item_summary['stats']
        item_stats_summary = extract_stats_detail(item_stats, language)
        item_default_stats_values = item_stats_summary['default']
        item_hidden_stats_values = item_stats_summary['hidden']
        
        item_sockets = item_summary['sockets']
        item_socket_summary = extract_socket_detail(item_sockets, language)
        for tmp in item_socket_summary:
            try:
                item = item_socket_summary[tmp]['socketIsPerk']
                if item:
                    item_perk_name = item_socket_summary[tmp]['socketName']
                    item_perk_description = item_socket_summary[tmp]['socketDescription']
                    item_perks = {
                        "name": item_perk_name,
                        "description": item_perk_description
                        }
            except KeyError:
                continue

        item_socket_stat_sum = item_socket_summary['socketStatSum']
        for name in item_socket_stat_sum:
            if name in item_default_stats_values:
                item_default_stats_values[name] += item_socket_stat_sum[name]
            elif name in item_hidden_stats_values:
                item_hidden_stats_values[name] += item_socket_stat_sum[name]
            else:
                item_default_stats_values[name] = 0
                item_default_stats_values[name] += item_socket_stat_sum[name]

        item_detail = {
            "itemHash": item_hash,
            "itemName": item_name,
            "itemRootType": item_root_category,
            "itemType": item_type,
            "itemDamageType": item_damage_type,
            "itemTier": item_tier_type,
            "itemDescription": item_description,
            "itemIcon": item_icon,
            "itemCategory": item_category_dict,
            "itemDefaultStats": item_default_stats_values,
            "itemHiddenStats": item_hidden_stats_values,
            "itemPerks": item_perks,
            "itemSockets": item_socket_summary
        }
        json_data = json.dumps(item_detail)
        return json_data

def extract_stats_detail(stat_data, language=DEFAULT_LANGUAGE): 
    default_stat_hashes = []
    item_default_stats_values = {}
    item_hidden_stats_values = {}
    item_stat_group_hash = stat_data['statGroupHash']
    item_default_stats = stat_data['stats']

    default_stat_group = get_destiny_entity_definition('DestinyStatGroupDefinition',item_stat_group_hash, language)
    for stats in default_stat_group['scaledStats']:
        stat_hash = stats['statHash']
        if stat_hash not in default_stat_hashes:
            default_stat_hashes.append(stat_hash)

    for item_stat in item_default_stats:
        stat_hash = item_default_stats[item_stat]['statHash']
        if stat_hash not in USELESS_STATS:
            try:
                stat_summary = get_destiny_entity_definition('DestinyStatDefinition', stat_hash, language)
                stat_name = stat_summary['displayProperties']['name']
                stat_value = item_default_stats[item_stat]['value']
                if stat_hash in default_stat_hashes:
                    if stat_name not in item_default_stats_values.keys():
                        item_default_stats_values[stat_name] = 0
                    item_default_stats_values[stat_name] += stat_value
                else:
                    if stat_name not in item_hidden_stats_values.keys():
                        item_hidden_stats_values[stat_name] = 0
                    item_hidden_stats_values[stat_name] += stat_value
            except KeyError:
                hoshino.logger.exception('KeyError for statHash {0}'.format(stat_hash))
                continue

    stats_values = {
        "default":item_default_stats_values,
        "hidden":item_hidden_stats_values
    }
    return stats_values

def extract_investment_stats(stats_data, language=DEFAULT_LANGUAGE):
    investment_stats_values = {}
    for stat in stats_data:
        stat_hash = stat['statTypeHash']
        if stat_hash not in USELESS_STATS:
            try:
                stat_summary = get_destiny_entity_definition('DestinyStatDefinition', stat_hash, language)
                stat_name = stat_summary['displayProperties']['name']
                stat_value = stat['value']
                if stat_name not in investment_stats_values.keys():
                    investment_stats_values[stat_name] = 0
                investment_stats_values[stat_name] += stat_value
            except KeyError:
                hoshino.logger.exception('KeyError for statHash {0}'.format(stat_hash))
                continue
    return investment_stats_values

def extract_socket_detail(socket_data, language=DEFAULT_LANGUAGE):
    socket_detail_dict = {}
    stat_sum = {}
    for socket in socket_data['socketEntries']:
        socket_hash = socket['singleInitialItemHash']
        socket_plug_sources = socket['plugSources']
        socket_is_perk = None
        try:
            res = get_destiny_entity_definition('DestinyInventoryItemDefinition', socket_hash, language)
            socket_name = res['displayProperties']['name']
            socket_description = res['displayProperties']['description']
            if res['displayProperties']['hasIcon']:
                socket_icon = 'https://www.bungie.net' + res['displayProperties']['icon']
            else:
                socket_icon = None
            socket_plug_category = res['plug']['plugCategoryIdentifier']
            if socket_plug_sources == 6 and socket_plug_category == "intrinsics":
                socket_is_perk = True
            if "energyCapacity" not in res['plug'].keys():
                socket_investment_stats = extract_investment_stats(res['investmentStats'], language)
                for name in socket_investment_stats:
                    if name not in stat_sum.keys():
                        stat_sum[name] = 0
                    stat_sum[name] += socket_investment_stats[name]
                socket_detail = {
                    "socketName": socket_name,
                    "socketDescription": socket_description,
                    "socketIcon": socket_icon,
                    "socketPlugSources": socket_plug_sources,
                    "socketPlugCategory": socket_plug_category,
                    "socketStats": socket_investment_stats,
                    "socketIsPerk": socket_is_perk
                }
                socket_detail_dict[socket_hash] = socket_detail
        except KeyError:
            hoshino.logger.exception('KeyError for statHash {0}'.format(socket_hash))
            continue
    socket_detail_dict["socketStatSum"] = stat_sum
    return socket_detail_dict

