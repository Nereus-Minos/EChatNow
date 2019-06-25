# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from mvc.models import Note, User, Category, Area, Chatmessage

from django.utils.translation import ugettext as _
from django.template import Context, loader

from EChat.settings import *
from utils import mailer, formatter, function, uploader


from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt

import datetime
import json

from PIL import Image


# Create your views here.
# home view
@csrf_exempt
def index(request):
    # get user login status
    _islogin = __is_login(request)
    flag = False
    _blogsinfo = []

    if _islogin:
        flag = True
        _template = loader.get_template('interface/inindex.html')
    else:
        _login_user = None
        # body content
        _template = loader.get_template('interface/index.html')

    if flag:
        for _note in Note.objects.filter(user=__user_id(request)):
            _bloginfo = []
            _bloginfo.append(_note.id)
            _bloginfo.append(_note.heads)
            _bloginfo.append(_note.message)
            _bloginfo.append(_note.addtime)
            _blogsinfo.append(_bloginfo)

    _context = {
        'flag': True,
        'blogsinfo': _blogsinfo,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)


# return user login status
def __is_login(request):
     return request.session.get('islogin', False)


# get session user id
def __user_id(request):
    return request.session.get('userid',-1)


# get session realname
def __user_name(request):
    return request.session.get('username','')


# 用户注册
@csrf_exempt
def signup(request):
    # check is login
    _islogin = __is_login(request)
    flag = False

    if (_islogin):
        return HttpResponseRedirect('/')

    _userinfo = {
        'username': '',
        'password': '',
        'confirm': '',
        'realname': '',
        'email': '',
    }

    try:
        # get post params
        _userinfo = {
            'username': request.POST['user_name'],
            'password': request.POST['pwd'],
            'confirm': request.POST['cpwd'],
            'realname': request.POST['user_name'],
            'email': request.POST['email'],
        }
        _is_post = True
    except (KeyError):
        _is_post = False

    if (_is_post):
        _state = __do_signup(request, _userinfo)
    else:
        _state = {
            'success': False,
            'message': _('注 册')
        }

    if (_state['success']):

        return signin(request)

    if(_state['message'] == '用户已存在！'):
        flag = True

    _result = {
        'success': _state['success'],
        'message': _state['message'],
        'form': {
            'username': _userinfo['username'],
            'realname': _userinfo['realname'],
            'email': _userinfo['email'],
        }
    }

    # body content
    _template = loader.get_template('interface/register.html')
    _context = {
        'page_title': _('注册'),
        'state': _result,
        'flag': flag,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# post signup data
def __do_signup(request, _userinfo):
    _state = {
        'success': False,
        'message': '',
    }
    try:
        _user = User.objects.get(username=_userinfo['username'])
        _state['success'] = False
        _state['message'] = '用户已存在！'
    except (User.DoesNotExist):
        _user = User(
            username=_userinfo['username'],
            realname=_userinfo['realname'],
            password=_userinfo['password'],
            email=_userinfo['email'],
            area=Area.objects.get(id=1)
        )
        _user.save()
        _state['success'] = True
        _state['message'] = _('成功！')

    # send regist success mail
    mailer.send_regist_success_mail(_userinfo)

    return _state


# signin view
@csrf_exempt
def signin(request):
    # get user login status
    _islogin = __is_login(request)

    try:
        # get post params
        _username = request.POST['user_name']
        _password = request.POST['pwd']
        _is_post = True
    except (KeyError):
        _is_post = False

    # check username and password
    if _is_post:
        _state = __do_login(request, _username, _password)

        if _state['success']:
            return index(request)
    else:
        _state = {
            'success': False,
            'message': _('请先登录！')
        }

    # body content
    _template = loader.get_template('interface/land.html')
    _context = {
        'page_title': _('Signin'),
        'state': _state,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# do login
def __do_login(request, _username, _password):
    _state = __check_login(_username, _password)
    if _state['success']:
        # save login info to session
        request.session['islogin'] = True
        request.session['userid'] = _state['userid']
        request.session['username'] = _username
        request.session['realname'] = _state['realname']

    return _state


# check username and password
def __check_login(_username, _password):
    _state = {
        'success': True,
        'message': 'none',
        'userid': -1,
        'realname': '',
    }

    try:
        _user = User.objects.get(username=_username)

        # to decide password
        if (_user.password == function.md5_encode(_password)):
            _state['success'] = True
            _state['userid'] = _user.id
            _state['realname'] = _user.realname
        else:
            # password incorrect
            _state['success'] = False
            _state['message'] = _('Password incorrect.')
    except (User.DoesNotExist):
        # user not exist
        _state['success'] = False
        _state['message'] = _('User does not exist.')

    return _state


# signout view
@csrf_exempt
def signout(request):
    request.session['islogin'] = False
    request.session['userid'] = -1
    request.session['username'] = ''

    return HttpResponseRedirect('/')


# 个人资料配置
@csrf_exempt
def settings(request):
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
    except:
        return HttpResponseRedirect('/signin/')

    if request.method == "POST":
        # get post params
        _userinfo = {
            'realname': request.POST['realname'],
            'password': request.POST['password'],
            'confirm_password': request.POST['confirm_password'],
            'email': request.POST['email'],
            'face': request.POST['face_src'],
            "about": request.POST['about'],
        }
        _is_post = True
    else:
        _is_post = False

    _state = {
        'message': ''
    }

    # save user info
    if _is_post:
        if _userinfo['password'] == _userinfo['confirm_password']:
            _user.realname = _userinfo['realname']
            _user.email = _userinfo['email']
            _user.about = _userinfo['about']
            _file_obj = _userinfo['face']
            if _file_obj:
                _user.face = _file_obj
                print(_file_obj)
                print("*"*80)
            if _userinfo['password'] != '':
                _user.password = _userinfo['password']
                _user.save(True)
                _state['message'] = _('保存成功，密码已修改！')
            else:
                _user.save(False)
                _state['message'] = _('保存成功，密码未修改！')
        else:
            _state['message'] = _('密码与确认密码不匹配！')

    # body content
    _template = loader.get_template('interface/settings.html')
    _context = {
        'state': _state,
        'islogin': _islogin,
        'user': _user,
    }
    _output = _template.render(_context)
    return HttpResponse(_output)


# 设置中上传图片
@csrf_exempt
def upload_user_img(request):
    try:
        file = request.FILES['image']
        _up_state = uploader.upload_face(file, __user_id(request))
        return_url = '%sface_temporary/16/%s' % (MEDIA_URL, _up_state['message'])
        return HttpResponse(return_url)
    except Exception:
        return HttpResponse("error")


# 博客编写
def write_blog(request, _id, _username=''):
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    # body content
    _template = loader.get_template('interface/postform.html')

    user = User.objects.get(username=__user_name(request))

    try:
        search_content = request.path_info.split('/')[2]
    except:
        search_content = ''

    _this_url = request.path_info

    if '0' == _id:
        _note = None
    else:
        _note = get_object_or_404(Note, id=_id)

    _context = {
        'user': user,
        'search_content': search_content,
        'this_url': _this_url,
        'note': _note,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


# 富文本编辑中处理上传图片
@csrf_exempt  # 取消csrf验证，否则会有403错误
def upload_file(request, dir_name):
    files = request.FILES.get('upload_file')  # 得到文件对象
    today = datetime.datetime.today()

    sub_file_dir = 'upload_imgs' + '/%d/%d/%d/' % (today.year, today.month, today.day)
    file_dir = MEDIA_ROOT + sub_file_dir
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    # 修改图片大小
    im = Image.open(files)
    (x, y) = im.size  # read image size
    x_s = 50  # define standard width
    y_s = int(y * x_s / x)  # calc height based on standard width
    out = im.resize((x_s, y_s), Image.ANTIALIAS)  # resize image with high-quality
    out.save(file_dir + files.name)

    # 得到JSON格式的返回值
    upload_info = {"success": True, 'file_path': MEDIA_URL + sub_file_dir + files.name}
    upload_info = json.dumps(upload_info)

    return HttpResponse(upload_info, content_type="application/json")


# 富文本编辑器提交处理
@csrf_exempt
def handle_write_blog(request):
    # get user login status
    _islogin = __is_login(request)
    try:
        # get post params
        _message = request.POST['message']
        _message_head = request.POST['message_head']
        _is_post = True
    except (KeyError):
        _is_post = False

    # check login
    if not _islogin:
        return HttpResponseRedirect('/signin/')

    # save messages
    (_category, _is_added_cate) = Category.objects.get_or_create(name=u'网页')

    try:
        _user = User.objects.get(id=__user_id(request))
    except:
        return HttpResponseRedirect('/signin/')

    _note = Note(heads=_message_head, message=_message, category=_category, user=_user)
    _note.save()

    return blogs_show(request)


# 粗略全部博客展示
@csrf_exempt
def blogs_show(request):
    # get user login status
    _islogin = __is_login(request)
    flag = False

    _blogsinfo = []

    if _islogin:
        flag = True
        _template = loader.get_template('interface/inblog.html')
    else:
        _login_user = None
        # body content
        _template = loader.get_template('interface/outblog.html')

    if flag:
        for _note in Note.objects.filter(user=__user_id(request)):
            _bloginfo = []
            _bloginfo.append(_note.id)
            _bloginfo.append(_note.heads)
            _bloginfo.append(_note.message)
            _bloginfo.append(_note.addtime)
            _blogsinfo.append(_bloginfo)
    else:
        for _note in Note.objects.all():
            _bloginfo = []
            _bloginfo.append(_note.id)
            _bloginfo.append(_note.heads)
            _bloginfo.append(_note.message)
            _bloginfo.append(_note.addtime)
            _blogsinfo.append(_bloginfo)

    _context = {
        "blogsinfo": _blogsinfo,
    }
    _output = _template.render(_context)

    return HttpResponse(_output)


# 博客删除
def blog_delete(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)
    _note.delete()

    return blogs_show(request)


# 博客全文信息
def blog_detail(request, _id):
    # get user login status
    _islogin = __is_login(request)

    _note = get_object_or_404(Note, id=_id)

    # body content
    _template = loader.get_template('interface/blogDetail.html')

    _context = {
        'blog': _note,
        'islogin': _islogin,
        'userid': __user_id(request),
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


# 微聊列表模块
def users_list(request):
    # check is login
    _islogin = __is_login(request)

    _login_user = None
    _login_user_friend_list = None
    if _islogin:
        try:
            _login_user = User.objects.get(id=__user_id(request))
            _login_user_friend_list = _login_user.friend.all()

            # 所有人
            _users = User.objects.order_by('-addtime')
        except:
            _login_user = None

    else:
        _users = User.objects.order_by('-addtime')

    # body content
    _template = loader.get_template('interface/users_list.html')

    _context = {
        'users': _users,
        'userself': _login_user,
        'login_user_friend_list': _login_user_friend_list,
        'islogin': _islogin,
        'userid': __user_id(request),
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


# 添加好友   _username为好友的名字
def friend_add(request, _username):
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _state = {
        "success": False,
        "message": "",
    }

    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
        _friend = User.objects.get(username=_username)
        _user.friend.add(_friend)
        return users_list(request)
    except:
        return HttpResponse("你所访问的页面不存在",status=404)


# 删除好友
def friend_remove(request, _username):
    """
    summary:
        解除与某人的好友关系
    """
    # check is login
    _islogin = __is_login(request)

    if (not _islogin):
        return HttpResponseRedirect('/signin/')

    _state = {
        "success": False,
        "message": "",
    }

    _user_id = __user_id(request)
    try:
        _user = User.objects.get(id=_user_id)
        _friend = User.objects.get(username=_username)
        _user.friend.remove(_friend)
        return users_list(request)
    except:
        return HttpResponse("你所访问的页面不存在", status=404)


# 好友聊天界面
def friend_chat(request, _username):
    _user2friend = 'yes'
    _ischat = True
    friend_id = User.objects.get(username=_username).id
    user_id = __user_id(request)
    _islogin = __is_login(request)

    user_face = str(User.objects.get(id=user_id).face)
    friend_face = str(User.objects.get(id=friend_id).face)

    _messages = read_mysql_chat_message(user_id, friend_id)
    # print(type(_messages))
    # print(_messages)

    # body content
    _template = loader.get_template('interface/chat.html')

    _context = {
        'islogin': _islogin,
        'user_id': user_id,
        'friend_id': friend_id,
        'username': _username,
        'ischat': _ischat,
        'user_face': user_face,
        'friend_face': friend_face,
        'messages': _messages,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


# 轮询处理未读消息
def handle_chatMessage(request):
    '''
    request中有init则表示会话窗口才开启，得返回old_messages,否则表示为轮询查询
    以json格式返回
    :param request:
    :return:
    '''

    _user_id = __user_id(request)

    # 获取发送内容
    if request.method == 'GET':

        if request.GET.get('init') == 'yes':
            send_message = request.GET.get('send_message')
            _friend_id = request.GET.get('friend_id')
            _write_id = _user_id
            # 讲发送写入数据库
            _chatmessage = Chatmessage(message=send_message, write_id=_write_id,
                                       user_id=_user_id, friend_id=_friend_id)
            _chatmessage.save()

            return HttpResponse(json.dumps({'ok': 'ok'}))

        else:
            # 查询是否有新消息,按照时间查询
            _friend_id = request.GET.get('friend_id')
            messages = read_mysql_chat_message(_user_id, _friend_id, old=False)
            return HttpResponse(json.dumps({'messages': messages}))


# 返回聊天消息列表
def read_mysql_chat_message(_user_id, _friend_id, old=True):
    try:
        # 多个过滤器逐个调用表示逻辑与关系，同sql语句中where部分的and关键字。
        from django.db.models import Q
        if old:
            messages = [[messageall.write_id == int(_user_id), messageall.message] for messageall in
                       Chatmessage.objects.filter(Q(Q(user_id=_user_id) & Q(friend_id=_friend_id)) |
                                                  Q(Q(friend_id=_user_id) & Q(user_id=_friend_id)))
                           .filter(user_id__in=[_user_id, _friend_id])]
            # 将所有未读‘0’信息全部置为已读‘1’
            for messageall in Chatmessage.objects.filter(Q(Q(user_id=_friend_id) & Q(friend_id=_user_id))).filter(is_read=0):
                messageall.is_read = 1
                messageall.save()
        else:
            messages = []
            for messageall in Chatmessage.objects.filter(Q(Q(friend_id=_user_id) & Q(user_id=_friend_id))).filter(is_read=0):
                messages.append(messageall.message)
                messageall.is_read = 1
                messageall.save()
    except:
        messages = '数据库查询错误'
    return messages


# 搜索
def searching(request):
    # body content
    _template = loader.get_template('searching.html')

    _go_back_url = function.get_referer_url(request)

    _context = {
        'ischat': True,
        'go_back_url': _go_back_url,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)


@csrf_exempt
def searching_handle(request):
    if 'search_content' in request.POST:
        search_content = request.POST['search_content']
        go_back_url = request.POST['go_back_url']
    else:
        search_content = request.GET['search_content']
        go_back_url = request.GET['go_back_url']

    _islogin = __is_login(request)

    _login_user = None
    _userid = None

    if _islogin:
        _login_user = User.objects.get(username=__user_name(request))
        _userid = _login_user.id


    if search_content == '':
        return __result_message(request, _message=_('请输入搜索内容！'), _go_back_url=go_back_url)

    _searching_user = User.objects.filter(realname__contains=search_content)

    _searching_notes = Note.objects.filter(message__contains=search_content)

    # body content
    _template = loader.get_template('search_result.html')

    _context = {
        'islogin': _islogin,
        'userself': _login_user,
        'userid': _userid,
        'search_content': search_content,
        'searching_user': _searching_user,
        'searching_notes': _searching_notes,
        'go_back_url': go_back_url,
    }

    _output = _template.render(_context)

    return HttpResponse(_output)

