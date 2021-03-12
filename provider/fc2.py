import re

from lxml import etree

from utility.http import get_html


def getTitle(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = html.xpath('/html/head/title/text()')[0]
    return result


def getActor(content: str) -> str:
    try:
        html = etree.fromstring(content, etree.HTMLParser())
        result = html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')[0]
        return result
    except:
        return ''


def getStudio(content: str) -> str:  # 获取厂商
    try:
        html = etree.fromstring(content, etree.HTMLParser())
        result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/ul/li[3]/a/text()')).strip(" ['']")
        return result
    except:
        return ''


def getID(content: str) -> str:  # 获取番号
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('/html/body/div[5]/div[1]/div[2]/p[1]/span[2]/text()')).strip(" ['']")
    return result


def getRelease(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[2]/div[2]/p/text()')).strip(
        " ['販売日 : ']").replace('/', '-')
    return result


def getCover(content: str) -> str:
    html = etree.fromstring(content, etree.HTMLParser())
    result = str(html.xpath('//*[@id="top"]/div[1]/section[1]/div/section/div[1]/span/img/@src')).strip(" ['']")
    return 'http:' + result


def getTags(number: str) -> list[str]:
    content = str(bytes(get_html('http://adult.contents.fc2.com/api/v4/article/' + number + '/tag?'), 'utf-8').decode(
        'unicode-escape'))
    result = re.findall('"tag":"(.*?)"', content)
    return result


def getImages(content: str) -> list[str]:  # 获取剧照
    hr = re.compile(r'<ul class=\"items_article_SampleImagesArea\"[\s\S]*?</ul>')
    html = hr.search(content)
    if html:
        html = html.group()
        hf = re.compile(r'<a href=\"(.*?)\"')
        return hf.findall(html)
    return []


def main(number: str) -> dict:
    number = number.replace('FC2-', '').replace('fc2-', '')
    content = get_html('https://adult.contents.fc2.com/article/' + number + '/')
    actor = getActor(content)
    if getActor(content) == '':
        actor = 'FC2系列'
    metadata = {
        'title': getTitle(content),
        'studio': getStudio(content),
        'outline': '',  # getOutline(content),
        'runtime': '',
        'director': getStudio(content),
        'actor': actor,
        'release': getRelease(content),
        'id': 'FC2-' + number,
        'label': '',
        'cover': getCover(content),
        'images': getImages(content),
        'tags': getTags(number),
        'actor_photo': '',
        'website': 'https://adult.contents.fc2.com/article/' + number + '/',
        'source': 'fc2',
        'series': '',
    }
    return metadata


if __name__ == '__main__':
    print(main('FC2-1603395'))
