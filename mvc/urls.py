from django.conf.urls import url
from mvc import views


urlpatterns = [
    url(r'^$', views.index),        # 主页,登陆后首页不一样,里面包含全部博客展示
    url(r'^signup/$', views.signup),         # 注册
    url(r'^signin/$', views.signin),         # 登录
    url(r'^signout/$', views.signout),        # 退出登录
    url(r'^settings/$', views.settings, name='settings'),  # 个人中心设置
    url(r'^upload_img/$', views.upload_user_img, name='upload_user_img'),  # 个人中心中上传头像
    url(r'^write_blog/(?P<_id>\d+)/$', views.write_blog, name="write_blog"),  # 写微说ss
    url(r'^handle_write_blog/$', views.handle_write_blog),  # 处理写微说函数
    url(r'^myadmin/upload/(?P<dir_name>)', views.upload_file),  # 处理富文本编辑起中的上传图像
    url(r'^blogs_show/$', views.blogs_show),        # 粗略全部博客展示或个人博客展示
    url(r'^message/(?P<_id>\d+)/delete/$', views.blog_delete, name="blog_delete"),  # 删除空间消息
    url(r'^message/(?P<_id>\d+)/detail/$', views.blog_detail, name="blog_detail"),     # 发布的空间信息详情

    url(r'^users_list/$', views.users_list),        # 微聊列表
    url(r'^friend/add/(?P<_username>[a-zA-Z\-_\d\u4E00-\u9FA5]+)', views.friend_add, name="friend_add"),# 已登录用户信息,添加好友, _username为好友的名字
    url(r'^friend/remove/(?P<_username>[a-zA-Z\-_\d\u4E00-\u9FA5]+)', views.friend_remove, name='friend_remove'),  # 已登录信息，删除好友
    url(r'^friend/chat/(?P<_username>[a-zA-Z\-_\d\u4E00-\u9FA5]+)', views.friend_chat, name="friend_chat"),  # chat
    url(r'handle_chatMessage/$', views.handle_chatMessage),  # 处理聊天

    url(r'searching/$', views.searching, name='EChat.mvc.views.searching'),    # 搜索函数
    url(r'searching_handle/$', views.searching_handle),    # 处理搜索函数
]
