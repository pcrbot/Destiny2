locationZhCht = {
    "earth":"地球·歐洲死區·曲折河灣地",
    "io":"木衛一·回音高原·巨人之痕",
    "nessus":"涅索斯·桃源山谷·守望者之墓",
    "titan":"土衛六·新太平洋生態園區·鑽井",
    "tower":"地球·高塔·機庫",
    "where is xûr?":"玖還在利維坦刷金裝..."
}

locationZhChs = {
    "earth":"地球·欧洲无人区·九曲湾",
    "io":"木卫一·厄科台地·巨人伤疤",
    "nessus":"涅索斯·阿卡狄亚谷·守望者之墓",
    "titan":"土卫六·新太平洋生态园区·钻井",
    "tower":"地球·高塔·机库",
    "where is xûr?":"老九还在利维坦刷狗关...",
}

def GetZhLangXurLocation(location, lang):
    if lang == 'zh-cht':
        zhChtLocation = locationZhCht[location]
        return zhChtLocation
    if lang == 'zh-chs':
        zhChsLocation = locationZhChs[location]
        return zhChsLocation