import requests
import json
import re
import urllib
import shutil
import wget
import os
import time

from bs4 import BeautifulSoup

messages = []
# limit = 30000
iteratio = int(0)


def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]


def domAll(url):
    html_text = requests.get(url).text
    return BeautifulSoup(html_text, 'html.parser')


def getUrl(str):
    regex = r"url\(\'(.*)\'\)"
    result = re.findall(regex, str)
    if result:
        return result[0]
    return 0


def download(url, file_path='./files/'):
    global isDownload

    if not isDownload:
        return

    if url:
        r = requests.get(url, allow_redirects=True)

        name = url.split('/')[-1]
        name = name[30:50]
        type = r.headers.get('content-type').split('/')[1]
        filename = '%s.%s' % (name, type)

        file = '%s%s' % (file_path, filename)
        if not os.path.exists(file_path):
            os.mkdir(file_path)

        with open(file, 'wb') as f:
            f.write(r.content)

        # Retrieve HTTP meta-data
        print(r)


def parseAll(url):
    global iteratio
    global limit
    global nameChanel
    # soup = domAll('https://t.me/s/prikotik')
    soup = domAll(url)
    # path = './%s/' % nameChanel
    path = './%s/' % 'zalip'

    # exit()
    # посилання на попередню сторінку
    prev_link = soup.find(rel="prev")

    # contents = soup.select('.tgme_channel_history .tgme_widget_message_wrap')
    contents = soup.findAll('div', {'class': 'tgme_widget_message_wrap'})
    contents.reverse()
    # print(soup)
    for content in contents:
        result = {}
        # посилання на повідомлення
        url = content.find('a')
        if url:
            result.update({"url": url.get('href')})
        # текст повідомлення
        text = content.find('div', {'class': 'tgme_widget_message_text'})
        if text:
            result.update({"text": text.text})

        # картинка повідомлення
        photo = content.find('a', {'class': 'tgme_widget_message_photo_wrap'})
        if photo:
            photo_url = getUrl(photo.get('style'))
            result.update({"photo": photo_url})
            download(photo_url, path)

        # кількість переглядів
        views = content.find('span', {'class': 'tgme_widget_message_views'})
        if views:
            result.update({"views": views.text})
        # Автор повідомлення
        author_name = content.find('div', {'class': 'tgme_widget_message_author'})
        if author_name:
            result.update({"author_name": author_name.find('span').text})
        # Посилання на  автора повідомлення
        author_url = content.find('div', {'class': 'tgme_widget_message_author'})
        if author_url:
            result.update({"author_url": author_url.find('a').get('href')})
        # дата та час публікації  повідомлення
        time = content.find('a', {'class': 'tgme_widget_message_date'}).find('time').get('datetime')

        result.update({"time": time})
        # група медіафайлів
        groupfiles = []
        medias = content.find('div', {'class': 'tgme_widget_message_grouped_layer'})
        if medias:
            for media in medias.findAll('a'):
                if media:
                    groupfiles.append({
                        'url': getUrl(media.get('style'))
                    })


            result.update({'media': groupfiles})

        # Відео
        video = content.find('a', {'class': 'tgme_widget_message_video_player'})
        if video:
            if video.find('i'):
                result.update({'video_thumb': getUrl(video.find('i').get('style'))})

            video_block = video.find('video')
            if video_block:
                video_url = video_block.get('src')
                result.update({'video_url': video_url})
                download(video_url, path)

        messages.append(result)

    print(prev_link)

    if prev_link and (limit != iteratio):
        iteratio = iteratio + 1
        parseAll('https://t.me%s' % prev_link.get('href'))

    return messages


print('Enter your nameChanel:')

nameChanel = input()

print('Limit Page:')
limit = input()

print('Download media? (1 - yes, 0 - no):')
isDownload = input()


res = parseAll('https://t.me/s/%s' % nameChanel)

# https://t.me/Pechenki_Blog
jsonString = json.dumps(res, ensure_ascii=False)
jsonFile = open("%s.json" % nameChanel, "w", encoding='utf8')
jsonFile.write(jsonString)
jsonFile.close()
