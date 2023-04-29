import tomllib
import requests

from bs4 import BeautifulSoup
from scrapy.selector import Selector
from lxml import html as lxhtml

from brightdata import proxy_servers


def get_social_xpath(filename="socials.toml"):
    socials = list()

    with open(filename, "rb") as f:
        data = tomllib.load(f)
    for name, item in data.items():
        socials.append({"name": name, **item})

    s = [f"contains(@href, '{site.get('domain')}')" for site in socials]
    s = " or ".join([f"contains(@href, '{site.get('domain')}')" for site in socials])
    s = f".//a[{s}]"

    return s


def get_html(url):
    response = requests.get(url, proxies=proxy_servers)
    assert response.status_code == 200
    html = response.text
    return html


def meta_info(url, soup=None):
    if not soup:
        html = get_html(url)
        soup = BeautifulSoup(html, features="lxml")

    tree = lxhtml.fromstring(html)

    # Get meta info
    tree_see_also = lxhtml.fromstring(html)
    see_also = tree_see_also.xpath("//meta[@property='og:see_also']/@content")
    for leaf in see_also:
        yield "meta-see-also", leaf

    twitter_site = tree.xpath("//meta[@name='twitter:site']/@content")
    for leaf in twitter_site:
        yield "meta-twitter-site", leaf

    icons = tree.xpath("//link[@rel='icon']/@href")
    for leaf in icons:
        yield "icons", leaf

    search = tree.xpath("//link[@rel='search']/@href")
    for leaf in search:
        yield "search", leaf

    alternate = tree.xpath("//link[@rel='alternate']/@href")
    for leaf in alternate:
        yield "oembed-json", leaf

    social_paths = tree.xpath(get_social_xpath())
    for leaf in social_paths:
        href = leaf.attrib.get("href")
        yield "body", href


if __name__ == "__main__":
    from pprint import pprint

    print(list(meta_info("https://bas.bio")))
    # pprint(list(meta_info("https://onesignal.com")))
    # pprint(list(meta_info("https://bas.codes/posts/this-week-python-059")))
