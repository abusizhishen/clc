# encoding=utf8
import os, sys
from requests import Session
from lxml import html
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

url = "http://www.clchuwai.com/travel/detail/%s#userjoin"
def ciyun(text, id):
    from os import path
    from wordcloud import WordCloud
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


def get_text(id):
    ss = Session()
    resp = ss.get(url=url % id)
    if resp.status_code == 302:
        exit("活动%s不存在" % id)

    tree = html.fromstring(resp.text, )
    node = tree.xpath("//ul[@class=\"list\"]//p")
    users = []
    for i in node:
        users.append(i.text)

    dom = BeautifulSoup(resp.text, 'lxml')
    div = dom.find_all("div", {"class": "sub-detail"})[1]
    content = div.text

    for i in find_leader(content, "【 领 队 】"):
        users.append(i)
    for i in find_leader(content, "【副领队】"):
        users.append(i)

    return users


def find_leader(content, type):
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


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        exit("请输入活动id")

    id = args[1]
    print("活动链接地址：", url % id)
    users = get_text(id)
    if len(users) == 0:
        exit("没有报名人员")
    else:
        print("总人数：", len(users))
    ciyun(" ".join(users), id)
