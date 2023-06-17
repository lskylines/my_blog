from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


def article_list(request):
    search = request.GET.get("search")
    order = request.GET.get("order")
    if search:
        if order == "total_views":
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            ).order_by("-total_views")
        else:
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search) |
                Q(body__icontains=search)
            )
    else:
        search = ""
        if order == "total_views":
            article_list = ArticlePost.objects.all().order_by("-total_views")
        else:
            article_list = ArticlePost.objects.all()

    # 修改每页显示2篇文章
    paginator = Paginator(article_list, 2)

    # 获取页码
    page = request.GET.get("page")
    articles = paginator.get_page(page)
    context = {"articles": articles, "order": order, "search": search}
    return render(request, "article/list.html", context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)

    # 浏览量 + 1
    article.total_views += 1
    article.save(update_fields=["total_views"])

    md = markdown.Markdown(extensions=[
                          # 包含缩写，表格等常用扩展
                          'markdown.extensions.extra',
                          # 语法高亮扩展
                          'markdown.extensions.codehilite',

                          # 目录扩展
                          "markdown.extensions.toc",
                      ])

    # 将Markdown语法渲染成HTML
    article.body = md.convert(article.body)
    context = {"article": article, "toc": md.toc}
    return render(request, "article/detail.html", context)


@login_required(login_url="/userprofile/login")
def article_create(request):
    if request.method == "POST":
        print("article create post....")
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交数据是否满足模型
        if article_post_form.is_valid():
            # 保存数据，暂不提交到数据库
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)
            new_article.save()

            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，重新填写")
    else:
        article_post_form = ArticlePostForm()
        context = {"article_post_form": article_post_form}
        return render(request, "article/create.html", context)


def article_delete(request, id):
    article = ArticlePost.objects.get(id=id)
    article.delete()
    return redirect("article:article_list")


@login_required(login_url="/userprofile/login/")
def article_safe_delete(request, id):
    if request.method == "POST":
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("你无权限删除文章")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


@login_required(login_url="/userprofile/login/")
def article_update(request, id):
    article = ArticlePost.objects.get(id=id)

    if request.user != article.author:
        return HttpResponse("你无权修改这篇文章")

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST["title"]
            article.body = request.POST["body"]
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误,请重新填写")
    else:
        article_post_form = ArticlePostForm()
        context = {"article": article, "article_post_form": article_post_form}
        return render(request, "article/update.html", context)
