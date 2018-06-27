import hashlib
import datetime
import time

from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from . import models, forms


# 定义生成确认码函数
def makeComfirmStr(user):
    nowTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashCode(user.name, nowTime)
    models.ConfirmString.objects.create(code=code, user=user)
    return code


# 定义发送邮件方法
def sendEmail(email, code):
    subject = '来自秋城夜话的注册确认邮件'

    text_content = '感谢注册本网站，来和我们一起吹牛逼。如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请联系管理员！'

    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>秋城夜话</a>，来和我们一起吹牛逼</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

    msg = EmailMultiAlternatives(
        subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 定义加密函数
def hashCode(s, salt='theFirst'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 首页
def index(request):
    return render(request, 'myKofan/index.html')


# 登录
def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = forms.UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = "您™还没有确认邮件!!!"
                    return render(request, 'myKofan/login.html', locals())
                if user.password == hashCode(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except:
                message = "用户不存在！"
        return render(request, 'myKofan/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'myKofan/login.html', locals())


# 注册
def register(request):
    if request.session.get("is_login", None):
        return redirect('/index/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "请检查填写的内容"
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            confirmPassword = register_form.cleaned_data['confirmPassword']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password != confirmPassword:
                message = "两次输入的密码不匹配!!"
                return render(request, 'myKofan/register.html', locals())
            else:
                sameUsername = models.User.objects.filter(name=username)
                if sameUsername:
                    message = "用户名已存在"
                    return render(request, 'myKofan/register.html', locals())
                sameEmail = models.User.objects.filter(email=email)
                if sameEmail:
                    message = "该邮箱已被注册"
                    return render(request, 'myKofan/register.html', locals())
                newUser = models.User()
                newUser.name = username
                newUser.password = hashCode(password)
                newUser.email = email
                newUser.save()

                # 生成确认码,发送确认邮件
                code = makeComfirmStr(newUser)
                sendEmail(email, code)
                message = "注册成功，请去邮箱确认"

                return render(request, 'myKofan/welcome.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'myKofan/register.html', locals())


# 退出
def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/index/")
    request.session.flush()
    return redirect('/index/')


# 确认邮件
def userConfirms(request):
    code = request.GET.get('code', None)
    message = ''
    try:
        confirm = models.ConfirmString.objects.get(code=code)
    except:
        message = '无效请求!'
        return render(request, 'myKofan/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.datetime.now()
    if now > c_time+datetime.timedelta(settings.CONFIRM_DAYS):
        confirm.user.delete()
        message = '确认邮件已过期请重新注册'
        return render(request, 'myKofan/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save()
        confirm.delete()
        message = "已确认成功，请登录"
        return render(request, 'myKofan/confirm.html', locals())


# 中转页面
def welcome(request):
    return render(request, 'myKofan/welcome.html')
