# -*- coding: utf-8 -*-
import hashlib

def md5_encode(str):
    u"""
    summary:
        MD5 encode
    author:
        Jason Lee <huacnlee@gmail.com>
    """
    return hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()

def get_referer_url(request):
    """
    summary:
        get request referer url address,default /
    author:
        Jason Lee <huacnlee@gmail.com>
    """
    return request.META.get('HTTP_REFERER', '/')