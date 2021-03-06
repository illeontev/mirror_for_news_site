import os
import re

from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://news.ycombinator.com/'
STATIC_URL = '/static/proxy_app/'


def find_words_with_6_letters(text):
    """Find unique words, that consists of 6 letters"""
    return set(re.findall(r'\b[A-zА-я]{6}\b', text))


def transform_text(text):
    """Add '™' to the end of every 6-letter word."""
    words = find_words_with_6_letters(text)
    new_text = text
    for word in words:
        new_text = new_text.replace(word, word + '™')
    return new_text


def generate_content(url=''):
    """Generate content for index.html."""
    r = requests.get(os.path.join(BASE_URL, url))

    # we use 'lxml' to prevent generating empty p-tags
    bs = BeautifulSoup(r.content, 'lxml')

    for tag in bs.find_all():

        # transform the text in tag if there is the text in tag
        # and if tag has no children (to prevent double transform)
        if tag.string and not tag.find_all():
            tag.string.replace_with(transform_text(tag.string))

        # change the link to css file
        if tag.name == 'link':
            if 'news.css' in tag['href']:
                tag['href'] = os.path.join(STATIC_URL, 'news.css')
            elif 'favicon.ico' in tag['href']:
                tag['href'] = os.path.join(STATIC_URL, 'favicon.ico')
        # change the link to css file
        elif tag.name == 'script' and 'hn.js' in tag['src']:
            tag['src'] = os.path.join(STATIC_URL, 'hh.js')
        # change the link to logo
        elif tag.name == 'img' and 'y18.gif' in tag['src']:
            tag['src'] = os.path.join(STATIC_URL, 'y18.gif')
        # change the base url in links on localhost
        elif tag.name == 'a' and BASE_URL[:-1] in tag['href']:
            tag['href'] = tag['href'].replace(BASE_URL[:-1], 'http://localhost:8000')
        # remove empty p tags, generated by the parser
        elif tag.name == 'p' and len(tag.get_text(strip=True)) == 0:
            tag.extract()

    return bs.decode()


def index(request, url):
    """Render the page, using generate_content()."""
    return render(
        request,
        'proxy_app/index.html',
        {'content': generate_content(url)},
    )
