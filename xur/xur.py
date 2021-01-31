from . import *
from .location import *
import asyncio

xur_cht_json_path = '/home/ubuntu/PurinBot/hoshino/modules/destiny2/xur/xur-cht.json'
xur_chs_json_path = '/home/ubuntu/PurinBot/hoshino/modules/destiny2/xur/xur-chs.json'

@sv.on_prefix(('老九在哪','xur','老9在哪','9在哪','老九位置'))
async def whereisxur(bot, ev):
    if is_xur_working_now():
        #url = "http://api.purinbot.cn/xur?lang=zh-cht"
        #xur_data = requests.request('GET', url, timeout=5).json()
        if ev.message.extract_plain_text() == '简':
            xur_data = load_xur_data('zh-chs')
        elif ev.message.extract_plain_text() == '繁':
            xur_data = load_xur_data('zh-cht')
        else:
            xur_data = load_xur_data(DEFAULT_LANGUAGE)
        location = xur_data['location']['name']
        weapon = weapon_detail(xur_data)
        armor = armor_detail(xur_data)
        armor = '\n'.join(armor)
        #days = when_xur_move(1).replace(' day, ','天').replace(':','时',1).replace(':','分',1) + '秒'
        days = when_xur_move(1)
        msg = f"XÛR目前在：\n【{location}】\n距离XÛR离开还有：\n【{days}】\n{'='*21}\n本周售卖的货物为：{weapon}{armor}"
        await bot.send(ev, msg)
    else:
        #days = when_xur_move(0).replace(' day, ','天').replace(':','时',1).replace(':','分',1) + '秒'
        days = when_xur_move(0)
        inaiMsg = f'老九还在和坦尼克斯对线，还有{days}才会回来哦'
        await bot.send(ev, inaiMsg, at_sender=True)

@sv.on_fullmatch(('更新老九','更新xur'))
async def update_xur(bot,ev):
    if priv.check_priv(ev,priv.SUPERUSER):
        for lang in LOAD_LANGUAGES:
            resp = await get_xur_sale_items(lang)
            items = json.loads(resp)
            location = get_xur_location()
            WriteXurInformation().xur_sale_items(items, lang)
            WriteXurInformation().xur_location(location)
        hoshino.logger.info('已更新Xur信息')
        await bot.send(ev, '已更新Xur信息')

@sv.scheduled_job('cron', hour='01', minute='03')
async def auto_update_xur():
    freq = 30
    for lang in LOAD_LANGUAGES:
        resp = await get_xur_sale_items(lang)
        items = json.loads(resp)
        location = get_xur_location()
        while location == "where is xûr?":
            count += freq
            if count >= 900: # 15分钟还没刷出来就离谱了
                break
            asyncio.sleep(freq)
            hoshino.logger.info('正在等待Xur位置...')
            location = get_xur_location()
        WriteXurInformation().xur_sale_items(items, lang)
        WriteXurInformation().xur_location(location)
    hoshino.logger.info('已更新Xur信息')
    await auto_broadcast_xur()

#@sv_bc.scheduled_job('cron',day_of_week='5', hour='01', minute='05')
async def auto_broadcast_xur():
    xur_data = load_xur_data(DEFAULT_LANGUAGE)
    location = xur_data['location']['name']
    weapon = weapon_detail(xur_data)
    armor = armor_detail(xur_data)
    armor = '\n'.join(armor)
    time = when_xur_move(1)
    #days = when_xur_move(1).replace(' day, ','天').replace(':','时',1).replace(':','分',1) + '秒'
    days = when_xur_move(1)
    msg = f"XÛR目前在：\n【{location}】\n距离XÛR离开还有：\n【{days}】\n{'='*21}\n本周售卖的货物为：{weapon}{armor}"
    await sv_bc.broadcast(msg, 'xur', 0.5)

def is_xur_working_now():
    hour = datetime.datetime.now().strftime('%H')
    day = datetime.datetime.now().strftime('%w')
    if day in ['4', '5'] or (day == '6' and int(hour) < 1) or (day == '3' and int(hour) > 0):
        return False
    else:
        return True

def when_xur_move(action) -> datetime.timedelta: # come:0 leave:1
    if action:
        cale = calendar.WEDNESDAY
    else:
        cale = calendar.SATURDAY
    timeNow = datetime.datetime.now()
    today = timeNow - datetime.timedelta(hours=timeNow.hour - 1, minutes=timeNow.minute, seconds=timeNow.second)
    oneday = datetime.timedelta(days = 1)
    while today.weekday() != cale:
        today += oneday
    atoTime = today - timeNow
    days = atoTime.days
    hours = atoTime.seconds // 3600
    minutes = (atoTime.seconds // 60) % 60
    ato_time_str = f'{days}天{hours}时{minutes}分'
    return ato_time_str

def armor_detail(json_data):
    armor_msg = []
    armor_detail = json_data['item']['armor']
    for tmp in armor_detail:
        item = armor_detail[tmp]
        item_name = item["name"]
        item_icon = f'[CQ:image,file={item["icon"]}]'
        item_type = item["type1"] + '·' + item["type2"]
        item_perk = f'【{item["perk"]["name"]}】{item["perk"]["description"]}'
        armor_msg.append(f"{'='*21}\n{item_icon}\n《{item_name}》：{item_type}\n{item_perk}")
    return armor_msg

def weapon_detail(json_data):
    weapon_detail = json_data['item']['weapon']
    for tmp in weapon_detail:
        item = weapon_detail[tmp]
        item_name = item["name"]
        item_icon = f'[CQ:image,file={item["icon"]}]'
        item_type = item["type1"] + '·' + item["type2"] + '·' + item["damageType"]
        item_perk = f'【{item["perk"]["name"]}】{item["perk"]["description"]}'
        weapon_msg = f'\n{item_icon}\n《{item_name}》：{item_type}\n{item_perk}\n'
    return weapon_msg

def get_xur_location():
    url = 'https://xur.wiki/'
    try:
        html = requests.request('GET',url,timeout=5).text
    except requests.exceptions.ConnectTimeout:
        hoshino.logger.error('XurLocation API TIMEOUT')
    soup = BeautifulSoup(html, 'lxml')
    xur_location = soup.h1.string.strip().lower()
    return xur_location

def load_xur_data(lang=LOAD_LANGUAGES): # 别骂辣，给公开的XurAPI用的，不然我也不想重新封装一遍json
    if lang == 'zh-cht':
        xurJsonPath = xur_cht_json_path
    elif lang == 'zh-chs':
        xurJsonPath = xur_chs_json_path
    else:
        return
    if os.path.exists(xurJsonPath):
        with open(xurJsonPath,"r",encoding='utf-8') as dump_f:
            try:
                xur_data = json.load(dump_f)
            except:
                xur_data = {}
    else:
        xur_data = {}
    return xur_data

def sava_xur_data(config, lang):
    if lang == 'zh-cht':
        xurJsonPath = xur_cht_json_path
    elif lang == 'zh-chs':
        xurJsonPath = xur_chs_json_path
    else:
        return    
    with open(xurJsonPath ,"w",encoding='utf-8') as dump_f:
        json.dump(config,dump_f,indent=4,ensure_ascii=False)

class WriteXurInformation:  # XurAPI只考虑提供简中和繁中
    def __init__(self):
        self.data_cht = load_xur_data('zh-cht')
        self.data_chs = load_xur_data('zh-chs')

    def xur_location(self, location):
        location_cht = GetZhLangXurLocation(location, 'zh-cht')
        location_chs = GetZhLangXurLocation(location, 'zh-chs')
        self.data_cht['location'] = {"name":location_cht}
        self.data_chs['location'] = {"name":location_chs}
        sava_xur_data(self.data_cht, 'zh-cht')
        sava_xur_data(self.data_chs, 'zh-chs')
    
    def xur_sale_items(self, items, language=DEFAULT_LANGUAGE):
        weapon_detail = {}
        armor_detail = {}
        for i in items:
            item = items[i]
            itemHash = item['itemHash']
            itemName = item['itemName']
            itemDescription = item['itemDescription']
            itemIcon = item['itemIcon']
            itemCategory = item['itemCategory']
            itemRootType = item['itemRootType']
            itemType = item['itemType']
            itemDamageType = item['itemDamageType']
            itemDefaultStats = item['itemDefaultStats']
            itemHiddenStats = item['itemHiddenStats']
            itemPerks = item['itemPerks']
            if '1' in itemRootType.keys(): # Is Weapon
                for key in itemCategory:
                    if key in ['2','3','4']:
                        weaponAmmoType = itemCategory[key]
                itemDefaultStats.update(itemHiddenStats)
                weapon_detail[itemHash] = {
                    "name": itemName,
                    "description": itemDescription,
                    "icon": itemIcon,
                    "type1": weaponAmmoType,
                    "type2": itemType,
                    "damageType": itemDamageType,
                    "stat": itemDefaultStats,
                    "perk": itemPerks
                }
            elif '20' in itemRootType.keys(): # Is Armor
                for key in itemCategory:
                    if key in ['21','22','23']:
                        armorChara = itemCategory[key]
                armor_stat_sum = sum(itemDefaultStats.values())
                armor_detail[itemHash] = {
                    "name": itemName,
                    "description": itemDescription,
                    "icon": itemIcon,
                    "type1": armorChara,
                    "type2": itemType,
                    "stat": itemDefaultStats,
                    "statSum": armor_stat_sum,
                    "perk": itemPerks
                }

        item_detail = {
            "weapon":weapon_detail,
            "armor":armor_detail
        }
        self.data_cht['item'] = item_detail
        sava_xur_data(self.data_cht, language)

