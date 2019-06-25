# -*- coding: utf-8 -*-
from django.template import Library
from mvc.models import *
from EChat.settings import *

register = Library()


def get_face_url(size,content):
    if content:
        return content
    else:
        return DEFAULT_FACE % (size)


def face16(content):
    return get_face_url(16,content)


def face24(content):
    return get_face_url(24,content)


def face32(content):
    return get_face_url(32,content)


def face(content):
    return get_face_url(75,content)


def blog_sub(content, blogDetail):
    content = content
    l = len(content)
    i = 0
    count = 0
    while i < l:
        if -1 != content.find("&nbsp;", i, i+6):
            count += 1
            i += 5
        elif -1 != content.find("<img ", i, i+5):
            count += 2
            i = content.find(">", i+5, l)
        elif -1 != content.find("<br>", i, i+4) or -1 != content.find("</p>", i, i+4):
            count = ((count // 50)+1) * 50
            i += 3
        elif -1 != content.find(">", i, l):
            i = content.find(">", i, l)
            while i+1 < l and content[i+1] != "<":
                i += 1
                if -1 != content.find("&nbsp;", i, i + 6):
                    i += 5
                count += 1
                if count >= 150:
                    break

        if count >= 150:
            break

        i += 1

    html_label = []
    back_html = content[0:i] + ' ...  ' + blogDetail
    l = len(back_html)
    i = 0

    # 补全残缺HTML
    while i < l:
        if -1 != content.find("<img ", i, i + 5):
            i = content.find(">", i+5, l)+1
        elif -1 != content.find("<br>", i, i+4):
            i = i+4
        elif -1 != content.find("<", i, l):
            i = content.find("<", i, l)
            if back_html[i+1] != '/':
                if back_html[i+1] == 'a':
                    i = content.find(">", i, l)+1
                    html_label.append('a')
                    continue
                j = content.find(">", i, l)
                html_label.append(back_html[i+1:j])
                i = j + 1
            else:
                j = content.find(">", i, l)
                html_label.pop()
                i = j + 1
        else:
            break

    for back_label in html_label:
        back_html += '</' + back_label + '>'

    return back_html


register.filter('face', face)
register.filter('face16', face16)
register.filter('face24', face24)
register.filter('face32', face32)

register.filter('blog_sub', blog_sub)


def user_url(username):
    return '%suser/%s' % (APP_DOMAIN,username)