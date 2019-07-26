import requests
from bs4 import BeautifulSoup
import re
from urllib.request import urlretrieve
from fontTools.ttLib import TTFont
from pyquery import PyQuery as pq


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/75.0.3770.100 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    return response.text


def parse_html_bs4(html):  # shi用bs4 不用css
    soup = BeautifulSoup(html, 'lxml')
    # print(soup.find_all(name='div', attrs={'class': "board-item-content"}))  # ResultSet 不可直接string
    a = soup.find_all(name='div', attrs={'class': "movie-item-info"})
    b = soup.find_all(name='div', attrs={'class': "movie-item-number wish"})
    # print(b)
    for i in range(len(a)):
        for j in a[i].find_all(name='p'):
            print(j.string)
        for k in b[i].find_all(name='p'):
            print(k.span.string)

    '''for i in soup.find_all(name='div'):
        for j in i.find_all(attrs={'class': "movie-item-info"}):
            for k in j.find_all(name='p',attrs={'class':'star'}):
                print(k.string)'''
                # print(j.find(name='p', attrs={'class':'star'}))


def parse_html_bs4_css(html):  #  使用bs4+css
    soup = BeautifulSoup(html, 'lxml')
    for i in soup.select('.board-item-content'):
        for j in i.select('.movie-item-info p'):
            print(j.string)
        for k in i.select('.movie-item-number p'):
            print(k.span.string)


def parse_html_pyquery(html):  # 使用pyquery读取内容
    doc = pq(html)
    a = doc('.board-item-content')
    print(a.text())


def change_font(text):  # 转化数字
    base_font = TTFont('base_font.woff')  # 生成基础字库表对应
    # base_font.saveXML('base_font.xml')   # 查看细节
    base_font_list = base_font.getGlyphOrder()[2:]  # 去除前两位获取所有编码
    base_dict = {
        'uniF62A': '0', 'uniF719': '5', 'uniF1D6': '3', 'uniEA34': '4',
        'uniE7F5': '8', 'uniEEF9': '9', 'uniEC1D': '6', 'uniF7B1': '2',
        'uniF4EB': '7', 'uniE571': '1'
    }  # 写出对应表
    items = 'http://' + re.findall('url\(\'//(.*?\.woff)', text)[0]  # 获取字体网站
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


def main():
    url = 'https://maoyan.com/board/6'
    # print(get_page(url))
    rsp = get_page(url)
    html = change_font(rsp)
    # print(html)
    parse_html_pyquery(html)


if __name__ == '__main__':
    main()
