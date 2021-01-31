from ..D2_API import *

rewards_ts = {
    "Astral Horizon (Shotgun)":1697682876,
    "The Scholar (Scout Rifle)":2478792241,
    "The Summoner (Auto Rifle)":1907698332,
    "The Summoner (Auto)":1907698332,
    "Tomorrow's Answer (Rocket Launcher)":958384347,
    "Tomorrow's Answer (Rocket)":958384347,
    "Exile's Curse (Fusion)":679281855,
    "Eye of Sol (Sniper Rifle)":3164743584,
    "Eye of Sol (Sniper)":3164743584,
    "The Summoner (Adept, Auto)":3514144928,
    "Astral Horizon (Adept, Shotgun)":532746994,
    "The Scholar (Adept, Scout)":2386979999,
    "Eye of Sol (Adept, Sniper)":3637570176,
    "Tomorrow's Answer (Adept, Rocket)":1366917989,
    "Exile's Curse (Adept, Fusion)":276080079,
    "Helmet":3448274439, #Bucket
    "Chest":14239492,
    "Arms":3551918588,
    "Legs":20886954,
    "Class Item":1585787867,
    "Targeting":1710791394,
    "Mag":1225726778,
    "Charge Time":744770875,
    "Accuracy":117884138,
    "Blast Radius":229003538,
    "Counterbalance":1525622117,
    "Draw Time":1885045197,
    "Handling":4278960718,
    "Impact":3208647503,
    "Projectile Speed":2299766748,
    "Range":299264772,
    "Reload":634781242,
    "Stability":400326442
}
maps_ts = {
    "The Dead Cliffs":"", 
    "The Burnout":"", 
    "The Anomaly":"", 
    "Widow's Court":"", 
    "Cauldron":"", 
    "Rusted Lands":"", 
    "Exodus Blue":"", 
    "Javelin-4":"", 
    "Midtown":"", 
    "Altar of Flame":"", 
    "Endless Vale":"", 
    "Distant Shore":"", 
    "Convergence":"", 
    "Pacifica":"", 
    "Wormhaven":"", 
    "Bannerfall":"",  
    "Meltdown":"", 
    "Radiant Cliffs":""
    }

def get_rewards_translation(rewards:dict, language=DEFAULT_LANGUAGE):
    for i in rewards:
        item = rewards[i]
        name = item['name']
        if name not in rewards_ts.keys():
            item['ts_name'] = name
            item['icon_url'] = None
        else:
            item_hash = rewards_ts[name]
            try:
                item_summary = get_destiny_entity_definition(entityType='DestinyInventoryItemDefinition', entityHash=item_hash, language=language)
                item['ts_name'] = item_summary["displayProperties"]["name"]
                if item_summary["displayProperties"]["hasIcon"]:
                    icon = item_summary["displayProperties"]["icon"]
                    item['icon_url'] = "https://www.bungie.net" + icon
                else:
                    item['icon_url'] = None
            except KeyError:
                try:
                    item_summary = get_destiny_entity_definition(entityType='DestinyInventoryBucketDefinition', entityHash=item_hash, language=language)
                    item['ts_name'] = item_summary["displayProperties"]["name"]
                    if item_summary["displayProperties"]["hasIcon"]:
                        icon = item_summary["displayProperties"]["icon"]
                        item['icon_url'] = "https://www.bungie.net" + icon
                    else:
                        item['icon_url'] = None
                except KeyError:
                    item['ts_name'] = name
                    item['icon_url'] = None
    return rewards
        
