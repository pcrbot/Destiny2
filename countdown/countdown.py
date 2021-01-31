from . import *

async def get_season_countdown(language=DEFAULT_LANGUAGE):
    season_detail_dict = {}
    season_detail = await get_current_season_detail(language=language)
    season_detail_dict['season_description'] = season_detail['displayProperties']['description']
    season_detail_dict['season_name'] = season_detail['displayProperties']['name']
    season_detail_dict['season_number'] = season_detail['seasonNumber']
    season_start_date = season_detail['startDate']
    season_end_date = season_detail['endDate']
    local = datetime.datetime.now().astimezone(tz=tz)
    end_date_dt = datetime.datetime.strptime(season_end_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(tz=tz)
    start_date_dt = datetime.datetime.strptime(season_start_date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc).astimezone(tz=tz)
    season_rest_time = end_date_dt - local
    season_detail_dict['season_rest_days'] = season_rest_time.days
    season_detail_dict['season_rest_hours'] = season_rest_time.seconds // 3600
    season_detail_dict['season_rest_minutes'] = (season_rest_time.seconds // 60) % 60
    season_passed_time = local - start_date_dt
    season_detail_dict['season_passed_days'] = season_passed_time.days
    season_detail_dict['season_passed_hours'] = season_passed_time.seconds // 3600
    season_detail_dict['season_passed_minutes'] = (season_passed_time.seconds // 60) % 60
    return season_detail_dict

def get_today_lostsectors_reward():
    maps = ["移民号","溪谷虚空","隐秘虚空","地堡E15","永劫地狱"]
    armors = ["腿部护甲","臂铠","胸部护甲","头盔"]
    now_time = datetime.datetime.now()
    root_time = datetime.datetime.strptime("2020-12-27 01:00:00", '%Y-%m-%d %H:%M:%S')
    during_time = now_time - root_time
    during_days = during_time.days
    index_1250_map = during_days % len(maps)
    index_1280_map = index_1250_map - 1
    index_1250_armor = during_days % len(armors)
    index_1280_armor = index_1250_armor - 1
    reward_detail = {}
    reward_detail["map_1250"] = maps[index_1250_map]
    reward_detail["map_1280"]= maps[index_1280_map]
    reward_detail["armor_1250"]= armors[index_1250_armor]
    reward_detail["armor_1280"] = armors[index_1280_armor]
    return reward_detail