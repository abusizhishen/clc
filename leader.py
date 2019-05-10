import os, sys
from requests import Session
from lxml import html
import matplotlib.pyplot as plt
from pymongo import MongoClient

url = "http://www.clchuwai.com/travel/detail/%s#userjoin"
def ciyun(text, id):
    from os import path
    from wordcloud import WordCloud
    # get data directory (using getcwd() is needed to support running example in generated IPython notebook)
    d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

    # Read the whole text.
    # Generate a word cloud image
    font = r'/font/font.ttf'
    wordcloud = WordCloud(font_path=font, width=600, height=600, max_font_size=40,
                          random_state=42, max_words=100).generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("%s.png" % id)


def get_text(id):
    ss = Session()
    resp = ss.get(url=url % id)
    if resp.status_code == 302 or resp.status_code == 404:
        return []

    tree = html.fromstring(resp.text)
    p = tree.xpath("//p/span")

    row = {
        "id":int(id),
        "address":p[0].text,
        "time":p[1].text,
        "cost":p[2].text[:len(p[2].text)-1],
        "pre_fee":p[3].text[:len(p[3].text)-1],
        "leader":p[4].xpath("a")[0].text,
        "status":p[7].text,

    }

    node = tree.xpath("//ul[@class=\"list\"]//p")
    users = []
    for i in node:
        users.append(i.text)
    row["users"] = users

    content = tree.xpath('//div[@class="sub-detail"]')
    row["desc"] = content[0].text
    row["leader-desc"] = content[1].text
    row["other"] = content[2].text
    row["plan"] = content[3].text
    row["fee_desc"] = content[4].text
    row['count'] = len(users)

    active_insert(row)
    return row

client = MongoClient('localhost', 27017)
db = client.clc
user = db.user
active = db.active

def active_insert(row):
    print(row)
    active.insert_one(row).inserted_id

def user_insert(row):
    user.insert_one(row).inserted_id


def get(name):
    user.insert_one({"name":name})

def crawler():
    for i in range(3000,3888):
        id = "%d" % i
        row = get_text(id)

def update():
    act = active.find({"leader": "风马"})



def query():
    print("近一年统计数据")
    success = 0
    fail = 0
    id = []
    info = {}
    act = active.find({"leader": "小元宝"})
    for i in act:
        i['id'] = int(i['id'])
        id.append(i['id'])
        info[i['id']] = i

    id.sort()

    users = {}
    for i in id:
        i = info[i]
        i['id'] = int(i['id'])
        plan = i['plan']
        pos_en = plan.find("(")
        post_cn = plan.find("（")
        pos = pos_en if pos_en < post_cn and pos_en > 0 else post_cn

        print("%d, 领队：%s, 地点：%s,时间：%s, 人数：%s, 链接地址：%s" % (i["id"], i["leader"], i['address'], plan[:pos], len(i['users']), url % str(i["id"])))

        if len(i['users']) > 0:
            success += 1
        else :
            fail +=1
        for user in i['users']:
            if user in users:
                users[user] += 1
            else:
                users[user] = 1


    print("总计：%d" % len(info))
    print("成形：%d" % success)
    print("失败:%d" % fail)

    print()
    print()
    print("粉丝榜:")
    a1_sorted_keys = sorted(users, key=users.get, reverse=True)
    for r in a1_sorted_keys:
        print(users[r],r)
        pass

if __name__ == '__main__':
    query()