import sys

from mechanicalsoup.stateful_browser import StatefulBrowser
sys.path.append('../')
import re
from lxml import etree
import json
from bs4 import BeautifulSoup
from ADC_function import *
# import sys
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, errors = 'replace', line_buffering = True)

def getTitle(a):
    html = etree.fromstring(a, etree.HTMLParser())
    browser_title = str(html.xpath("/html/head/title/text()")[0])
    return browser_title[:browser_title.find(' | JavDB')].strip()

def getActor(a):
    html = etree.fromstring(a, etree.HTMLParser())
    actors = html.xpath('//span[@class="value"]/a[contains(@href,"/actors/")]/text()')
    genders = html.xpath('//span[@class="value"]/a[contains(@href,"/actors/")]/../strong/@class')
    r = []
    idx = 0
    actor_gendor = config.getInstance().actor_gender()
    if not actor_gendor in ['female','male','both','all']:
        actor_gendor = 'female'
    for act in actors:
        if((actor_gendor == 'all')
        or (actor_gendor == 'both' and genders[idx] in ['symbol female', 'symbol male'])
        or (actor_gendor == 'female' and genders[idx] == 'symbol female')
        or (actor_gendor == 'male' and genders[idx] == 'symbol male')):
            r.append(act)
        idx = idx + 1
    return r

def getaphoto(url):
    html_page = get_html(url)
    img_prether = re.compile(r'<span class\=\"avatar\" style\=\"background\-image\: url\((.*?)\)')
    img_url = img_prether.findall(html_page)
    if img_url:
        return img_url[0]
    else:
        return ''

def getActorPhoto(html): #//*[@id="star_qdt"]/li/a/img
    actorall_prether = re.compile(r'<strong>演員\:</strong>\s*?.*?<span class=\"value\">(.*)\s*?</div>')
    actorall = actorall_prether.findall(html)

    if actorall:
        actoralls = actorall[0]
        actor_prether = re.compile(r'<a href\=\"(.*?)\">(.*?)</a>')
        actor = actor_prether.findall(actoralls)
        actor_photo = {}
        for i in actor:
            actor_photo[i[1]] = getaphoto('https://' + javdb_site + '.com'+i[0])

        return actor_photo

    else:
        return {}

def getStudio(a):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"片商")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"片商")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
    patherr = re.compile(r'<strong>片商\:</strong>[\s\S]*?<a href=\".*?>(.*?)</a></span>')
    pianshang = patherr.findall(a)
    if pianshang:
        result = pianshang[0].strip()
        if len(result):
            return result
    # 以卖家作为工作室
    html = etree.fromstring(a, etree.HTMLParser())
    try:
        result = str(html.xpath('//strong[contains(text(),"賣家:")]/../span/a/text()')).strip(" ['']")
    except:
        result = ''
    return result

def getRuntime(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"時長")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"時長")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').rstrip('mi')
def getLabel(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getNum(a):
    html = etree.fromstring(a, etree.HTMLParser())
    result1 = str(html.xpath('//strong[contains(text(),"番號")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"番號")]/../span/a/text()')).strip(" ['']")
    return str(result2 + result1).strip('+')
def getYear(getRelease):
    # try:
    #     result = str(re.search('\d{4}', getRelease).group())
    #     return result
    # except:
    #     return getRelease
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)\-.*?</span>')
    dates = patherr.findall(getRelease)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result

def getRelease(a):
    # html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    # result1 = str(html.xpath('//strong[contains(text(),"時間")]/../span/text()')).strip(" ['']")
    # result2 = str(html.xpath('//strong[contains(text(),"時間")]/../span/a/text()')).strip(" ['']")
    # return str(result1 + result2).strip('+')
    patherr = re.compile(r'<strong>日期\:</strong>\s*?.*?<span class="value">(.*?)</span>')
    dates = patherr.findall(a)
    if dates:
        result = dates[0]
    else:
        result = ''
    return result
def getTag(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/a/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total

    except:
        result = html.xpath('//strong[contains(text(),"類別")]/../span/text()')
        total = []
        for i in result:
            try:
                total.append(translateTag_to_sc(i))
            except:
                pass
        return total

def getCover_small(a, index=0):
    # same issue mentioned below,
    # javdb sometime returns multiple results
    # DO NOT just get the firt one, get the one with correct index number
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    try:
        result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@src")[index]
        if not 'https' in result:
            result = 'https:' + result
        return result
    except: # 2020.7.17 Repair Cover Url crawl
        try:
            result = html.xpath("//div[@class='item-image fix-scale-cover']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result
        except:
            result = html.xpath("//div[@class='item-image']/img/@data-src")[index]
            if not 'https' in result:
                result = 'https:' + result
            return result


def getTrailer(htmlcode):  # 获取预告片
    video_pather = re.compile(r'<video id\=\".*?>\s*?<source src=\"(.*?)\"')
    video = video_pather.findall(htmlcode)
    if video:
        if not 'https:' in video[0]:
            video_url = 'https:' + video[0]
        else:
            video_url = video[0]
    else:
        video_url = ''
    return video_url

def getExtrafanart(htmlcode):  # 获取剧照
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    result = []
    try:
        result = html.xpath("//article[@class='message video-panel']/div[@class='message-body']/div[@class='tile-images preview-images']/a[contains(@href,'/samples/')]/@href")
    except:
        pass
    return result
def getCover(htmlcode):
    html = etree.fromstring(htmlcode, etree.HTMLParser())
    try:
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/a/img/@src")[0]
    except: # 2020.7.17 Repair Cover Url crawl
        result = html.xpath("//div[contains(@class, 'column-video-cover')]/img/@src")[0]
    return result
def getDirector(a):
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"導演")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"導演")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')
def getOutline0(number):  #获取剧情介绍 airav.wiki站点404，函数暂时更名，等无法恢复时删除
    try:
        htmlcode = get_html('https://cn.airav.wiki/video/' + number)
        from WebCrawler.airav import getOutline as airav_getOutline
        result = airav_getOutline(htmlcode)
        return result
    except:
        pass
    return ''
def getOutline(number):  #获取剧情介绍
    from WebCrawler.javbus import getOutline as javbus_getOutline
    return javbus_getOutline(number)
def getSeries(a):
    #/html/body/section/div/div[3]/div[2]/nav/div[7]/span/a
    html = etree.fromstring(a, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
    result1 = str(html.xpath('//strong[contains(text(),"系列")]/../span/text()')).strip(" ['']")
    result2 = str(html.xpath('//strong[contains(text(),"系列")]/../span/a/text()')).strip(" ['']")
    return str(result1 + result2).strip('+').replace("', '", '').replace('"', '')

def main(number):
    # javdb更新后同一时间只能登录一个数字站，最新登录站会踢出旧的登录，因此按找到的第一个javdb*.json文件选择站点，
    # 如果无.json文件或者超过有效期，则随机选择一个站点。
    javdb_sites = ["javdb31", "javdb32"]
    debug =  config.getInstance().debug()
    try:
        # if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number).group():
        #     pass
        # else:
        #     number = number.upper()
        number = number.upper()
        javdb_cookies = {'over18':'1', 'theme':'auto', 'locale':'zh'}
        # 不加载过期的cookie，javdb登录界面显示为7天免登录，故假定cookie有效期为7天
        has_json = False
        for cj in javdb_sites:
            javdb_site = cj
            cookie_json = javdb_site + '.json'
            cookies_dict, cookies_filepath = load_cookies(cookie_json)
            if isinstance(cookies_dict, dict) and isinstance(cookies_filepath, str):
                cdays = file_modification_days(cookies_filepath)
                if cdays < 7:
                    javdb_cookies = cookies_dict
                    has_json = True
                    break
                elif cdays != 9999:
                    print(f'[!]Cookies file {cookies_filepath} was updated {cdays} days ago, it will not be used for HTTP requests.')
        if not has_json:
            javdb_site = secrets.choice(javdb_sites)
        if debug:
            print(f'[!]javdb:select site {javdb_site}')
        try:
            javdb_url = 'https://' + javdb_site + '.com/search?q=' + number + '&f=all'
            res, browser = get_html_by_browser(javdb_url, cookies=javdb_cookies, return_type='browser')
            if not res.ok:
                raise
            query_result = res.text
        except:
            query_result = get_html('https://javdb.com/search?q=' + number + '&f=all', cookies=javdb_cookies)
        html = etree.fromstring(query_result, etree.HTMLParser())  # //table/tr[1]/td[1]/text()
        # javdb sometime returns multiple results,
        # and the first elememt maybe not the one we are looking for
        # iterate all candidates and find the match one
        urls = html.xpath('//*[@id="videos"]/div/div/a/@href')
        # 记录一下欧美的ids  ['Blacked','Blacked']
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            correct_url = urls[0]
        else:
            ids = html.xpath('//*[@id="videos"]/div/div/a/div[contains(@class, "uid")]/text()')
            try:
                correct_url = urls[ids.index(number)]
            except:
                # 为避免获得错误番号，只要精确对应的结果
                if ids[0].upper() != number:
                    raise ValueError("number not found")
                correct_url = urls[0]
        try:
            if isinstance(browser, StatefulBrowser):  # get faster benefit from http keep-alive
                detail_page = browser.open_relative(correct_url).text
            else:
                javdb_detail_url = 'https://' + javdb_site + '.com' + correct_url
                detail_page = get_html(javdb_detail_url, cookies=javdb_cookies)
        except:
            detail_page = get_html('https://javdb.com' + correct_url, cookies=javdb_cookies)

        # no cut image by default
        imagecut = 3
        # If gray image exists ,then replace with normal cover
        if re.search(r'[a-zA-Z]+\.\d{2}\.\d{2}\.\d{2}', number):
            cover_small = getCover_small(query_result)
        else:
            try:
                cover_small = getCover_small(query_result, index=ids.index(number))
            except:
                # if input number is "STAR438" not "STAR-438", use first search result.
                cover_small = getCover_small(query_result)
        if 'placeholder' in cover_small:
            # replace wit normal cover and cut it
            imagecut = 1
            cover_small = getCover(detail_page)

        dp_number = getNum(detail_page)
        if dp_number.upper() != number:
            raise ValueError("number not found")
        title = getTitle(detail_page)
        if title and dp_number:
            number = dp_number
            # remove duplicate title
            title = title.replace(number, '').strip()

        dic = {
            'actor': getActor(detail_page),
            'title': title,
            'studio': getStudio(detail_page),
            'outline': getOutline(number),
            'runtime': getRuntime(detail_page),
            'director': getDirector(detail_page),
            'release': getRelease(detail_page),
            'number': number,
            'cover': getCover(detail_page),
            'cover_small': cover_small,
            'trailer': getTrailer(detail_page),
            'extrafanart': getExtrafanart(detail_page),
            'imagecut': imagecut,
            'tag': getTag(detail_page),
            'label': getLabel(detail_page),
            'year': getYear(detail_page),  # str(re.search('\d{4}',getRelease(a)).group()),
            'actor_photo': getActorPhoto(detail_page),
            'website': 'https://javdb.com' + correct_url,
            'source': 'javdb.py',
            'series': getSeries(detail_page),

        }
        if not dic['actor'] and re.match(r'FC2-[\d]+', number, re.A):
            dic['actor'].append('素人')
            if not dic['series']:
                dic['series'] = dic['studio']
            if not dic['label']:
                dic['label'] = dic['studio']


    except Exception as e:
        if config.getInstance().debug():
            print(e)
        dic = {"title": ""}
    js = json.dumps(dic, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ':'), )  # .encode('UTF-8')
    return js

# main('DV-1562')
# input("[+][+]Press enter key exit, you can check the error messge before you exit.\n[+][+]按回车键结束，你可以在结束之前查看和错误信息。")
if __name__ == "__main__":
    config.G_conf_override['debug_mode:switch'] = True
    # print(main('blacked.20.05.30'))
    # print(main('AGAV-042'))
    # print(main('BANK-022'))
    print(main('070116-197'))
    print(main('093021_539'))  # 没有剧照 片商pacopacomama
    print(main('FC2-2278260'))
    print(main('FC2-735670'))
    # print(main('FC2-1174949')) # not found
    print(main('MVSD-439'))
    # print(main('EHM0001')) # not found
    print(main('FC2-2314275'))
