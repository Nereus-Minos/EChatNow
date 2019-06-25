mvc:为实现网站应用的主体内容；
mvc/templatetags:自定义过滤器，使用管道符号|来应用过滤器，用于进行计算、转换操作，可以使用在变量、标签中。
utils:为工具库文件；
utils/formatter.py中pagebar函数为分页条


templates:为动态模型存放文件；
templates/control:为生成HTML分页控件,要使用tempate
templates/include:在index.html中使用{% include}标签进行子模板嵌入，用于显示每一条消息



static:为静态文件存放文件；
static/media:为上传文件；


‘’’
    首先插入一条地区的数据库insert into mvc_area (name,code,type,parent) values ('China','+86',0,0);

‘’‘



'''遇到CSRF验证失败. 请求被中断.'''

1.在views.py中加from django.views.decorators.csrf import csrf_exempt，并在函数前面加@csrf_exempt
2.在模板中form下面加{%csrf_token%}
'''遇到CSRF验证失败. 请求被中断.''''


'''文本国际化''''

需要安装gettext

需要警醒下面配置
在settings.py中：

    MIDDLEWARE_CLASSES = (
    ...
    'django.middleware.locale.LocaleMiddleware',
    )

    # 国际文本化
    LANGUAGES = (
        ('en', ('English')),
        ('zh-cn', ('中文简体')),
        ('zh-tw', ('中文繁體')),
    )

    #  更改语言文件的位置
    LOCALE_PATHS = (
        os.path.join(BASE_DIR, 'conf/locale'),
    )

    使用python manage.py makemessages -l en来生成需要翻译的文件

    手工翻译 locale 中的 django.po
        (用msgid表达带翻译的文本内容， 用msgstr表达翻译后的文本内容)

    使用python manage.py compilemessages  编译一下，这样翻译才会生效

    如果翻译不生效，请检查你的语言包的文件夹是不是有 中划线，请用下划线代替它。比如 zh-hans 改成 zh_hans （但是要注意 setttings.py 中要用 中划线，不要也改了，就这一句话，你可能会浪费几个小时或几天）

'''文本国际化'''



'''首页页面显示'''
基本页面为base.html
首页页面为index.html继承base.html
    其中{% block  main %}为主体部分
        表单内容在include/postform.html中定义
        在视图函数中为模板传入参数note和page_bar，他们分别保存了消息 条目模型数据和分页条视图
        消息子模板为include/list_item.html
        分页条page_bar在formatter.pagebar_()函数中调用的模板control/home_pagebar.html或control/user_pagebar.html
'''首页'''


'''用户注册'''

用户注册调用的是views.py中的signup函数，所使用的htmml模板为signup.htmml
    （可以在signup.html中看到提交响应函数也是signup函数，并且没有使用ajax）
    函数功能能解析：
        1.首先通过__is_login()函数通过sessio数据来判断登录与否，如果已经登录则重定向到首页
        2.__do_signup()函数是实际处理注册操作的函数
        3.__do_signup()注册成功后在signup函数中调用__result_message函数返回模板result_message.html

用户密码使用的是md5进行加密的，在utils/function.py中md5_encode函数进行加密

'''用户注册'''


'''用户登录'''

用户登录调用过程与用户注册类似，与用户注册共用一个__result_message

'''用户登录'''


'''已登录的用户上线后'''

在登录首页时在index.html中调用了userinfo.html
    在settings.py中设置默认的用户图像DEFAULT_FACE = '/statics/images/face%d.png'
    在userinfo.html中通过{{ user.face|face }}调用templatetags/user_tags.py中的get_face_url函数获取默认用户图像

''''


''''设置''''

调用的是settings.html模板，提交后响应views.py中的settings函数更改数据库中的内容
    调用工具函数utils/uploader.py中的upload_face()函数将头像文件对象保存到服务器的文件系统中，该函数将保存的路径保存在返回值的"message"中。
    将文件路径赋予_user.face属性，并通过_user.save()函数保存在数据库中。

在图像上传那儿采用了ajax和隐形的file输入框：
    <td><img src="{{ user.face|face24 }}" class="face24" alt="{% trans 'My face' %}" id="user_face"/></td>
    <td><input type="button" value="图片" id="upload_images"></td>
    <input type="file" id="imageFileUpload" style="display: none" name="face">
当button按下时使#imageFileUpload自动按下调用，给人的感觉就是按下button打开的上传，当上传确认按钮确认后将#user_face的src属性换为上传图像的临时保存地址
    $("#editor_picture").on('click','#upload_images',function(){
        $("#imageFileUpload").trigger("click");
        $("#imageFileUpload").change(function(){
            var fileUploadControl = document.getElementById("imageFileUpload");
            var localFile = fileUploadControl.files[0];
            if (/.(gif|jpg|jpeg|png|bmp)$/.test(localFile.name)){
                var formData = new FormData();
                formData.append("image", localFile);
                $.ajax({
                    url: '{% url 'upload_user_img' %}',
                    type: 'POST',
                    data: formData,
                    cache: false,
                    contentType: false,
                    processData: false,
                    success: function (data) {
                        $("#user_face").attr("src",data);
                    },
                    error:function () {
                        alert('图片上传失败')
                    }
                });
            }
            else {
                alert('只能上传图片')
            }
        });
    });


''''设置''''


'''写微说''''
调用函数write_blog.调用的模板是postform.html。通过handle_write_blog处理提交请求，显示用户个人微说主页

在这里必须填写标题才能提交

    在这里因为tinyMCE功能强大，但是对手机的支持不好，而simditor对移动端的支持非常友好，但是功能不行。

    '''PC端，采用富文本编辑器tinyMCE，调用的是postform1.html'''
    （不用安装安装包）
    1.引入必要js
    从 https://www.tinymce.com/download/ 下载tinyMCE的社区版
    从 https://www.tinymce.com/download/language-packages/ 下载汉化文件，放到langs目录中
    2.在html中使用，并用ajax来控制图片上传
    <script type="text/javascript" src='/static/js/tinymce.min.js'></script>
    <script type="text/javascript">
        tinyMCE.init({
            selector: 'textarea',
            theme: "modern",
            plugins: "spellchecker,directionality,paste,image",
            file_browser_callback_types: 'image',
            file_picker_callback: function(callback, value, meta) {
                if (meta.filetype === 'image') {
                    var fileUploadControl = document.getElementById("imageFileUpload");
                    fileUploadControl.click();
                    fileUploadControl.onchange = function () {
                        if (fileUploadControl.files.length > 0) {
                            var localFile = fileUploadControl.files[0];
                            if (/.(gif|jpg|jpeg|png|bmp)$/.test(localFile.name)){
                                var formData = new FormData();
                                formData.append("image", localFile);
                                $.ajax({
                                    url: '{% url 'upload_img' %}',
                                    type: 'POST',
                                    data: formData,
                                    cache: false,
                                    contentType: false,
                                    processData: false,
                                    success: function (data) {
                                        callback(data, {alt: localFile.name});
                                    },
                                    error:function () {
                                        alert('图片上传失败')
                                    }
                                });
                            }
                            else {
                                alert('只能上传图片')
                            }
                        } else {
                            alert('请选择图片上传')
                        }
                    }
                }
            },
            convert_urls :false,
            language: "zh_CN",
            image_advtab: true,
            paste_data_images:true
        });
    </script>
    3.在views.py函数中添加处理图片相应的函数
    from django.conf import settings
    from django.views.decorators.csrf import csrf_exempt
    from PIL import Image

    @csrf_exempt
    def report_upload(request):
        try:
            file = request.FILES['image']
            img = Image.open(file)
            try:
                file_name = str(uuid.uuid1()).replace("-", "") + os.path.splitext(file.name)[1]
                img.save(os.path.join(settings.MEDIA_ROOT, "imgs", file_name), img.format)
                return HttpResponse(settings.MEDIA_URL + 'imgs/{0}'.format(file_name))
            except Exception:
                return HttpResponse("error")
        except Exception:
            return HttpResponse("error")
    4.在views.py中的handle_write_blog函数中保存html代码，禁止转义
    '''PC端，采用富文本编辑器tinyMCE，调用的是postform1.html'''


    '''移动端采用的是simditor，调用的是postform.html'''
    1.首先这个模板没有继承base.html，采用的是HTML5 移动页面自适应手机屏幕
        <meta name="viewport" content="width=device-width,initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no"/>

    2.使用simditor。
    <link rel="stylesheet" type="text/css" href="/static/js/simditor-2.3.5/styles/simditor.css" />
    <script type="text/javascript" src="/static/js/jquery-3.3.1.min.js"></script>
    <script type="text/javascript" src="/static/js/simditor-2.3.5/scripts/module.js"></script>
    <script type="text/javascript" src="/static/js/simditor-2.3.5/scripts/hotkeys.min.js">
    </script><script type="text/javascript" src="/static/js/simditor-2.3.5/scripts/uploader.js">
    </script><script type="text/javascript" src="/static/js/simditor-2.3.5/scripts/simditor.js"></script>
        <script>
            $(function() {

                var editor = new Simditor({
                        textarea: $('#editor_textarea'),
                        toolbarFloat: false,
                        upload:{
                        url:'/myadmin/upload/files', /* 注意myadmin前面的斜杠不能省掉，这是相对于根目录的*/
                            filekey:'upload_file', /* 相当于html标签里面的name值 */
                        },
                });
            });
        </script>

    3.在urls.py中添加：
        url(r'^myadmin/upload/(?P<dir_name>)', views.upload_file),         # 处理富文本编辑起中的上传图像

    4.在views.py中添加upload_file函数


    '''移动端采用的是simditor，调用的是postform.html'''



'''写微说''''


'''通讯录'''

  '''聊天''' 
    
   方法一:使用轮训方式
    1.点击聊天调用views.friend_chat
        查询数据库将和此朋友以往的聊天记录全部查询出来，返回聊天界面chat.html
    2.在chat.html中使用ajax来响应发送消息按钮
        将文本信息发送给后端views.handle_chatMessage保存信息，并将is_read字段设为0，表示未读消息
    3.在chat.html中设置周期为0.5秒的定时器，每次都使用ajax请求views.handle_chatMessage是否有新的消息(is_read字段设为0表示新消息)
    
    
   （未用）方法二:使用websocket建立长连接  
    1.调用views.friend_chat
    2.采用的是channels技术,建立websocket长连接
        '''
            channels技术:
            1.在settings.py中添加:
                INSTALLED_APPS = [
                    ....
                    'channels',
                ]
                        ....
                # channels配置
                ASGI_APPLICATION = 'tmitter.routing.application'    
                # Channels
                CHANNEL_LAYERS = {
                    'default': {
                        'BACKEND': 'channels_redis.core.RedisChannelLayer',
                        'CONFIG': {
                            "hosts": [('127.0.0.1', 6379)],
                        },
                    },
                }
            2.在根目录下建立routing.py,当有websocket连接进来时就调用它,
            在这个文件下,是连接转到mvc.routing.py下
            3.在mvc下建立routing.py,在这里当有连接进来时调用consumers.ChatConsumer
            4.在mvc下建立consumers.py文件,并创建ChatConsumer类,
            当有连接连接时自动调用类中的connect方法等等,都是自动调用的.
        '''
    3.在consumers.py中的receive函数中存储消息
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            _write_id = text_data_json['own']
            _chatmessage = Chatmessage(message=message, write_id=_write_id,
                                       user_id=self._user_id, friend_id=self._friend_id)
            _chatmessage.save()  
    4.在每次打开聊天界面时加载聊天记录，在connect函数中调用read_mysql_chat_message函数
        如何做到区分自己和朋友的聊天呢？
             我采用的是用messageall.write_id == int(self._user_id)即数据库中的write是不是现在的user，这就是为什么要建立一个write_id字段  
    5.
            # 问题如何解决未读消息呢
            # 初始想法：连接时获取一个时间，结束时获取一个时间，上一次结束时间到这次连接时间段所有friend_id==self._user_id的为未读消息
            # 所以需要建立一个模型专门存储最新的连接时间和结束时间
            
            
  '''聊天'''

'''通讯录'''



'''搜索'''
点击head的伪输入框，调用searching函数，跳转到searching.html页面，提交后调用searching_handle函数。
(注意：在取名字时不能用handle_search来命名views函数)
如果输入框为空则返回搜索之前的页面。

'''搜索'''



////
others
'''
    # test:获取用户ip
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META[HTTP_X_FORWARDED_FOR]
    else:
        ip = request.META['REMOTE_ADDR']
    print(ip)
    print('*'*30)
'''