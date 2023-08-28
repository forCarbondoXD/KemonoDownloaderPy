import os.path
import re

import requests as requests
from bs4 import BeautifulSoup

url = ["https://kemono.su", "https://kemono.party"]


def procNlTl(s):
    try:
        return s.replace("\n", "").replace("    ", "")
    except:
        return s

class HtmlParser:
    def __init__(self, url):
        self.url = url
        self.request_du = requests.get(self.url)
        self.request_du.encoding = 'utf-8'
        self.request_du_text = self.request_du.text
        self.htmlparser = BeautifulSoup(self.request_du_text, 'html.parser')

class KemonoDownloader:
    def __init__(self, download_type, url, download_url, downpath, basehome):
        self.download_type = download_type
        self.url = url
        self.download_url = download_url
        self.basehome = basehome
        self.down_path = self.basehome + downpath
        self.request_du = requests.get(self.download_url)
        self.request_du.encoding = 'utf-8'
        self.request_du_text = self.request_du.text
        self.htmlparser = BeautifulSoup(self.request_du_text, 'html.parser')

    def getElementByRegex(self, element):
        matchab = re.search(element, self.request_du_text)
        if matchab:
            return matchab.group(1)
        else:
            return ""

    def getElementByBs4(self, element):
        return self.htmlparser.get(element)

    class setup_info:
        @staticmethod
        def setupSetInfo(htmlparser):
            title = procNlTl(htmlparser.find("title").get_text())
            author = procNlTl(htmlparser.find("a", attrs={"class": "post__user-name"}).get_text())
            attars = []
            for i in htmlparser.find_all("div", attrs={"class": "post__thumbnail"}):
                attars.append(i.find("a").get("href"))
            pubtime = procNlTl(htmlparser.find("time", attrs={"class": "timestamp"}).get_text().replace("  ", "").replace(":", "_"))
            return {"title": title, "author": author, "attars": attars, "pubtime": pubtime}

        @staticmethod
        def setupUserInfo(htmlparser):
            works = []
            for work in htmlparser.find_all("article", attrs={"class": "post-card post-card--preview"}):
                works.append(
                    {
                        "title": procNlTl(work.find("a").find("header", attrs={"class": "post-card__header"}).get_text()),
                        "href": work.find("a").get("href"),
                        "thumbnail": procNlTl(work.find("a").find("div", attrs={"class": "post-card__image-container"}).find("img", attrs={"class": "post-card__image"}).get("src")),
                        "calendar": procNlTl(work.find("a").find("footer", attrs={"class": "post-card__footer"}).find("time", attrs={"class": "timestamp"}).get_text()),
                        "attachment": procNlTl(work.find("a").find("footer", attrs={"class": "post-card__footer"}).find("div").get_text())
                     })
            return works

    def download_sets(self, downlist_info):
        for i in range(0, len(downlist_info)):
            this = downlist_info[i]
            this_path = f"""{this["title"].replace(" | Kemono  ", "").replace('"', '')} {this["pubtime"]}"""
            downpath = f"""{self.down_path}/{this_path}"""

            if os.path.exists(downpath) is False:
                os.mkdir(downpath)

            print(f"""Downloading Tasks: {this['title']} as {this_path} at {downpath}""")

            thisattars = this["attars"]

            headers = {
                "Accept": "image/gif, image/jpeg, image/pjpeg, application/x-ms-application, application/xaml+xml, application/x-ms-xbap, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-Hans-CN,zh-Hans;q=0.8,en-US;q=0.5,en;q=0.3",
                "Host": "httpbin.org",
                "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; Tablet PC 2.0; wbx 1.0.0; wbxapp 1.0.0; Zoom 3.6.0)",
                "X-Amzn-Trace-Id": "Root=1-628b672d-4d6de7f34d15a77960784504"}

            for j in range(0, len(thisattars)):
                jthisattars = thisattars[j].split("?")
                jthisattars = [jthisattars[0], jthisattars[1].replace("f=", "")]
                print(f"Downloading {jthisattars}")
                try:
                    with open(f'{downpath}/{jthisattars[1]}', 'wb') as ff:
                        req = requests.get(jthisattars[0], headers=headers)
                        ff.write(req.content)
                        ff.flush()
                        req.close()
                        ff.close()
                except:
                    print(f"Skipping {jthisattars}, ERR")

if __name__ == '__main__':
    downmode = input("by (user/set): ")
    downurl = input("url: ")

    if downmode == "user":
        if downurl[-1] == "/":
            downurl = downurl[:-1]
        dllist = downurl.split('/')
        print(downurl)
        downpathmix = f"""{dllist[-3]}{dllist[-2]}{dllist[-1]}"""
        print(downpathmix)

        kmdu = KemonoDownloader("user", url[0], downurl, downpathmix, "./")

        if os.path.exists(kmdu.basehome + '/' + kmdu.down_path) is False:
            os.mkdir(kmdu.basehome + '/' + kmdu.down_path)

        pagefirst = kmdu.setup_info.setupUserInfo(kmdu.htmlparser)
        thislist = []
        for i in range(0, len(pagefirst)):
            this = pagefirst[i]
            thislist.append(this)
            print(f"""{i}. {this["title"]} at {this["calendar"]} | {this["attachment"]}""")
        down_count = len(pagefirst)
        print(f"    [{down_count - 1} sets in total]")
        which_down = input(f"""  [SELECT TO DOWNLOAD(all, 0..{down_count - 1})]: """)
        downlist = []
        if "," in which_down:
            downlist = which_down.split(",")
        elif ".." in which_down:
            dd = which_down.split("..")
            downlist = list(range(int(dd[0]), int(dd[1])+1))
        elif which_down == "all":
            downlist = list(range(0, down_count))
        elif " " in which_down:
            downlist = which_down.split()
        else:
            downlist = [int(which_down)]

        downlist_info = []
        for i in range(0, len(downlist)):
            downlist_info.append(kmdu.setup_info.setupSetInfo(HtmlParser(f"""{kmdu.url}/{thislist[int(downlist[i])]["href"]}""").htmlparser))

        kmdu.download_sets(downlist_info)
    else:
        kmd = KemonoDownloader(downmode, url[0], downurl, "", "./")
        print(kmd.getElementByRegex(r'<title>([^"]+)</title>'))
        print(kmd.setup_info.setupSetInfo(kmd.htmlparser))

