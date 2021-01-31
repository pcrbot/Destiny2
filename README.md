# Destiny2 Plugins For HoshinoBot

基于BungieAPI开发的命运2游戏插件集合

由于目前API的封装尚未完成,可能会对现有插件进行改动

请注意,插件会将Manifest文件写入内存,使用多语言占用内存会更大(启动Bot也会更慢)

一边学py一边写的插件,差不多能用就行(逃)

## 开始使用

0. `D2_API.py`文件是对BungieAPI的封装，`D2_MANIFEST.py`是对Destiny2 Manifest文件的处理，可以基于`D2_API`自行编写新的功能

1. 在HoshinoBot的modules目录下克隆本项目: 
   ``` BASH
   git clone https://github.com/pcrbot/Destiny2.git
   ```

2. 参考注释修改配置模板 destiny2.py.example 将其移动至HoshinoBot的统一配置目录之下后进行重命名
   ``` BASH
   vim ./destiny2.py.example
   mv ./destiny2.py.example ~/hoshino/config/destiny2.py
   ```

3. 在`~/hoshino/config/__bot__.py`里加入destiny2模块并重启HoshinoBot
   ```python
   MODULES_ON = {
     destiny2,
   }
   ```

4. 由于要下载Manifest文件并处理 所以启用模块后初次启动HoshinoBot会卡在下载数据，请耐心等待
   
## TODO

- [x] Manifset
  - [x] 定时自动更新
  - [x] 启动时自检修复
  - [ ] 
- 玩家搜索绑定
  - [x] 结果直接作用于战绩查询
  - [ ] 昵称更新或提醒绑定
  - [x] SteamID转换查询
  - [x] SteamID64, SteamID3, SteamID, Steam自定义url互转
  - [x] Steam用户名查询SteamID(仅限Steam命运2玩家)
- 战绩
  - [x] PVP战绩概览(ELO, KD等)
  - [ ] 详细分块战绩
  - [ ] RaidReport(刚准备写就新赛季了...)
  - [ ] 屁威屁乐子列表
- 周报
  - [x] Xur自动更新及推送
  - [x] 试炼周报自动更新及推送
  - [ ] 周报图片生成
- 杂项
  - [x] 当前赛季倒计时
  - [x] 传说遗失区域查询
  - [ ] 物品模糊查询
  - [ ] 传说故事插件
  - [ ] 简繁互译
  - [ ] 名片更新/查询
- [ ] LFG
- [ ] Oauth2.0
  - [ ] Vendor
  - [ ] ItemManager
