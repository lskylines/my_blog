from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
#引入验证登录的装饰器
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


# Create your views here.


def user_login(request):
    if request.method == "POST":
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # 清洗出合法数据
            data = user_login_form.cleaned_data
            # 校验账号密码是否匹配数据库中某个用户
            user = authenticate(username=data['username'], password=data["password"])
            if user:
                #将用户数据保存在session中
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("输入的账号密码有误")
        else:
            return HttpResponse("账号密码不合法")
    elif request.method == "GET":
        user_login_form = UserLoginForm()
        context = {"form": user_login_form}
        return render(request, "userprofile/login.html", context)
    else:
        return HttpResponse("请使用Get/POST请求")


def user_logout(reqest):
    logout(reqest)
    return redirect("article:article_list")


def user_register(request):
    if request.method == "POST":
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data["password"])
            new_user.save()
            login(request, new_user)
            return redirect("article:article_list")
        else:
            return HttpResponse("注册表单输入有误。请重新输入...")
    elif request.method == "GET":
        user_register_form = UserRegisterForm()
        context = {"form": user_register_form}
        return render(request, "userprofile/register.html", context)
    else:
        return HttpResponse("请使用GET/POST请求")


@login_required(login_url="/userprofile/login")
def user_delete(request, id):
    if request.method == "POST":
        user = User.objects.get(id=id)
        if request.user == user:
            login_required(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作权限")
    else:
        return HttpResponse("仅接受post请求")


