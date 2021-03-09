import requests
from bs4 import BeautifulSoup
import threading
import json


class Parser(object):
    def __init__(self):
        self.all_product = []
        self.threads = []
        self.a = []
        self.give_all_product()
        self.start()
        for thread in self.threads:
            thread.join()
        r = open("data.json", "w")
        r.write(json.dumps(self.a, indent=4))

    def give_all_product(self):
        r = requests.get("https://www.makita.ru/data/pam/sitemap/sitemap-1-1.xml")
        bs = BeautifulSoup(r.text, 'lxml')
        for link in bs.findAll("url"):
            url = link.find("loc").text
            if url.find("/product/") != -1:
                self.all_product.append(url)

    def start(self):
        for product in self.all_product:
            t = threading.Thread(
                target=self.HandlerPageProdct,
                args=(product,)
            )
            self.threads.append(t)
            t.start()
            self.wait_threads()

    def wait_threads(self):
        if len(self.threads) == 49:
            for thread in self.threads:
                thread.join()
            self.threads = []

    def HandlerPageProdct(self, product):
        s = {}
        pr = requests.get(product)
        soup = BeautifulSoup(pr.text, "html.parser")
        chara = soup.find("div", "barcode-container").find("div").text
        if len(chara) == 0:
            chara = "None"
        desc = soup.find("div", "product-description--marketing-text")
        if not desc:
            desc = "None"
        else:
            desc = desc.text.strip()
        print(chara)
        name = soup.find("div", "product-title")
        tech = soup.findAll("div", "techspecs-content-inner")
        for char in tech:
            s[char.find("div", "techspecs--row-specification").text.strip()] \
                = char.find("div", "techspecs--row-value").text.strip()
            if char.find("i", "fa-check"):
                s[char.find("div", "techspecs--row-specification").text.strip()] = "Да"
        self.a.append({
            "href": product,
            "name": name.find("h1").text.strip(),
            "desc": desc,
            "barcode": chara,
            "chara": s,
        })


Parser()
