# encoding=utf8

import os
import sys
import fire

import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from lxml import html
from requests import Session
from pymongo import MongoClient
from os import path
from wordcloud import WordCloud


def RedirectStdout(newStdout=sys.stdout):
    def decorator(func):
        def wrapper(*args, **kwargs):
            savedStdout, sys.stdout = sys.stdout, newStdout
            try:
                return func(*args, **kwargs)
            finally:
                sys.stdout = savedStdout

        return wrapper

    return decorator


class Clc:
    def __init__(self):
        self.url_detail = "http://www.clchuwai.com/travel/detail/%s#userjoin"

    def ciyun(self, text, id):
        # get data directory (using getcwd() is needed to support running example in generated IPython notebook)
        d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()

        # Read the whole text.
        # Generate a word cloud image
        font = r'./msyh.ttf'
        wordcloud = WordCloud(font_path=font, width=800, height=800, max_font_size=40,
                              random_state=42, max_words=100).generate(text)

        # Display the generated image:
        # the matplotlib way:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig("%s.png" % id)

    def get_text(self, id):
        ss = Session()
        resp = ss.get(url=self.url_detail % id)
        if resp.status_code == 302 or resp.status_code == 404:
            exit("活动%s不存在" % id)

        tree = html.fromstring(resp.text, )
        node = tree.xpath("//ul[@class=\"list\"]//p")
        users = []
        for i in node:
            users.append(i.text)

        dom = BeautifulSoup(resp.text, 'lxml')
        div = dom.find_all("div", {"class": "sub-detail"})[1]
        content = div.text

        for i in self.find_leader(content, "【 领 队 】"):
            users.append(i)
        for i in self.find_leader(content, "【副领队】"):
            users.append(i)

        return users

    def find_leader(self, content, type):
        arr = content.split(type)
        users = []
        if len(arr) > 1:
            for i in range(len(arr)):
                str = arr[i]
                find1 = str.find(",")
                find2 = str.find("，")

                l = []
                if find1 != -1:
                    l.append(find1)
                if find2 != -1:
                    l.append(find2)

                leader = str[:l[0]]
                users.append(leader)

        return users

    def signList(self, id):
        print("活动链接地址：", self.url_detail % id)
        users = self.get_text(id)
        if len(users) == 0:
            exit("没有报名人员")
        else:
            print("总人数：", len(users))
        self.ciyun(" ".join(users), id)

    # def ciyun(self,text, id):
    #     from os import path
    #     from wordcloud import WordCloud
    #     # get data directory (using getcwd() is needed to support running example in generated IPython notebook)
    #     d = path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    #
    #     # Read the whole text.
    #     # Generate a word cloud image
    #     font = r'/font/font.ttf'
    #     wordcloud = WordCloud(font_path=font, width=600, height=600, max_font_size=40,
    #                           random_state=42, max_words=100).generate(text)
    #
    #     # Display the generated image:
    #     # the matplotlib way:
    #     plt.imshow(wordcloud, interpolation='bilinear')
    #     plt.axis("off")
    #     plt.savefig("%s.png" % id)

    def get_text(self, id):
        ss = Session()
        resp = ss.get(url=self.url_detail % id)
        if resp.status_code == 302 or resp.status_code == 404:
            return []

        tree = html.fromstring(resp.text)
        p = tree.xpath("//p/span")

        row = {
            "id": int(id),
            "address": p[0].text,
            "time": p[1].text,
            "cost": p[2].text[:len(p[2].text) - 1],
            "pre_fee": p[3].text[:len(p[3].text) - 1],
            "leader": p[4].xpath("a")[0].text,
            "status": p[7].text,

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

        self.active_insert(row)
        return row

    client = MongoClient('localhost', 27017)
    db = client.clc
    user = db.user
    active = db.active

    def active_insert(self, row):
        print(row)
        self.active.insert_one(row).inserted_id

    def user_insert(self, row):
        self.user.insert_one(row).inserted_id

    def get(self, name):
        self.user.insert_one({"name": name})

    def crawler(self, ):
        for i in range(3000, 3888):
            id = "%d" % i
            row = self.get_text(id)

    def update(self, ):
        act = self.active.find({"leader": "风马"})

    file = open('leaderData.txt', "w")
    @RedirectStdout(file)
    def leaderData(self, name):
        print("近一年统计数据")
        success = 0
        fail = 0
        id = []
        info = {}
        act = self.active.find({"leader": name})
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

            print("%d, 领队：%s, 地点：%s,时间：%s, 人数：%s, 链接地址：%s" % (
                i["id"], i["leader"], i['address'], plan[:pos], len(i['users']), self.url_detail % str(i["id"])))

            if len(i['users']) > 0:
                success += 1
            else:
                fail += 1
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
            print(users[r], r)
            pass


def main():
    fire.Fire(Clc)


if __name__ == '__main__':
    main()
