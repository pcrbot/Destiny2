from . import *
from .translate import *

def trn_playlist_search(identifier, season):
    playlist = []
    url = 'https://api.tracker.gg/api/v2/destiny-2/standard/profile/steam/' + identifier + '/segments/playlist?season=' + season
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url, timeout=5, proxies=PROXIES).json()
        #resp = requests.request('GET', url, timeout=5).json()
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
        hoshino.logger.error(f'TRN数据查询请求出错,错误信息为{e}')
        errmsg = {'errmsg': f'玩家数据查询失败，错误信息为{e},请检查后重试或联系维护人员'}
        playlist.append(errmsg)
        return playlist

def trn_playlist_nametrans(name):
    if name not in play_list_name_ts:
        return name
    name_ts = play_list_name_ts[name]
    return name_ts

def trn_rank_nametrans(name):
    if name not in rank_name_ts:
        return name
    name_ts = rank_name_ts[name]
    return name_ts

async def get_season_now():
    season_detail = await get_current_season_detail()
    season_num = season_detail['seasonNumber']
    return season_num