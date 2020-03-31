# clc
和草履虫相关的一些趣味工具
### python3
###1.signList 生成某个活动的报名列表词云    

```shell script
# 如 链接地址 http://www.clchuwai.com/travel/detail/5415#userjoin
# 5415 为活动id
# 用法 python3 clc.py funName args

# 示例 : 
# 获取参加5415活动的虫子的词云图
python3 clc.py signList 5415 
# 词云文件为 {id}.png

# 生成某领队近一年的活动列表和粉丝榜 注 "风马"为领队名 
python3 clc.py leaderData 风马
# 数据见 leaderData.txt
```
