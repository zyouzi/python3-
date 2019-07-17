import requests
import re
import json
import time
from urllib.request import urlretrieve
from fontTools.ttLib import TTFont
from requests.exceptions import RequestException


def get_one_page(url):  # 获取网页
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36'
        }  # 模拟浏览器
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def change_font(text):  # 转化数字
    base_font = TTFont('base_font.woff')  # 生成基础字库表对应
    # base_font.saveXML('base_font.xml')   # 查看细节
    base_font_list = base_font.getGlyphOrder()[2:]  # 去除前两位获取所有编码
    base_dict = {
        'uniF62A': '0', 'uniF719': '5', 'uniF1D6': '3', 'uniEA34': '4',
        'uniE7F5': '8', 'uniEEF9': '9', 'uniEC1D': '6', 'uniF7B1': '2',
        'uniF4EB': '7', 'uniE571': '1'
    }  # 写出对应表
    items = 'http://' + re.findall('url\(\'//(.*?\.woff)', text)[0] # 获取字体网站
    filename = items.split('/')[-1]  # 生成新字体文件名
    urlretrieve(items, filename)
    new_font = TTFont(filename)
    new_font_list = new_font.getGlyphOrder()[2:]
    new_map = {}  # 对应表
    for uni2 in new_font_list:
        obj2 = new_font['glyf'][uni2]   # glyf xml文件中的 感觉类似数组a[1][x] = y
        for uni1 in base_font_list:
            obj1 = base_font['glyf'][uni1]
            if obj1 == obj2:
                new_map[uni2] = base_dict[uni1]
    # print(new_map)
    for i in new_map:
        pattern = '&#x' + i[3:].lower() + ';'
        #  print(pattern, new_map[i])
        text = re.sub(pattern, new_map[i], text)
        # 疑问  为啥这里将text改成改成其他的会失败?
    # print(text)
    return text


def parse_one_page(html): # 获取信息
    pattern = re.compile('<dd>.*?board-index.*?>(.*?)</i>.*?<a href="(.*?)" title="(.*?)".*?"star">(.*?)</p>.*?>(.*?)'
                         '</p>.*?month-wish">(.*?)<span>.*?stonefont">(.*?)</span>.*?>(.*?)</p>.*?total-wish">(.*?)'
                         '<span>.*?stonefont">(.*?)</span></span>(.*?)</p>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            '排名': item[0],  # 基于本月增长人数
            '链接': 'maoyan.com' + item[1],
            '名称': item[2],
            '演员': item[3].strip()[3:] if len(item[3]) > 3 else '',
            '时间': item[4].strip()[5:],
            '本月新增想看人数': item[6] + '人',
            '总想看人数': item[9] + '人',
        }
    # print(items)


def write_to_file(context):
    with open('result.txt', 'a', encoding='utf-8') as f:
        print(type(json.dumps(context)))
        f.write(json.dumps(context, ensure_ascii=False)+'\n')


def main(offset):
    url = 'https://maoyan.com/board/6?offset=' + str(offset)
    rsp = get_one_page(url)
    # change_font(rsp)
    #  print(rsp)
    html = change_font(rsp)
    for item in parse_one_page(html):
        print(item)
        write_to_file(item)


if __name__ == '__main__':
    for i in range(5):
        main(offset=i * 10)
        time.sleep(1)  # 延时等待
