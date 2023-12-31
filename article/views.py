from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from comment.forms import CommentForm

def article_list(request):
    search = request.GET.get("search")
    order = request.GET.get("order")
    column = request.GET.get("column")
    tag = request.GET.get("tag")
    article_list = ArticlePost.objects.all()

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) | Q(body__icontains == search)
        )
    else:
        search = ""

    # 栏目查询
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询
    if tag and tag != "None":
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == "total_views":
        article_list = article_list.order_by('-total_views')

    # 修改每页显示2篇文章
    paginator = Paginator(article_list, 8)
    # 获取页码
    page = request.GET.get("page")
    articles = paginator.get_page(page)
    context = {"articles": articles, "order": order, "search": search, "column": column, "tag": tag}
    return render(request, "article/list.html", context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)

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

    # 引入评论表单
    Comment_form = CommentForm()
    context = {"article": article, "toc": md.toc, "comments": comments, "comment_form": Comment_form}
    return render(request, "article/detail.html", context)


@login_required(login_url="/userprofile/login")
def article_create(request):
    if request.method == "POST":
        print("article create post....")
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交数据是否满足模型
        if article_post_form.is_valid():
            # 保存数据，暂不提交到数据库
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST["column"] != "none":
                new_article.column = ArticleColumn.objects.get(
                    id=request.POST["column"])
            new_article.save()

            # 标签多对多关系保存
            article_post_form.save_m2m()

            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，重新填写")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {"article_post_form": article_post_form, "columns": columns}
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
            if request.POST["column"] != "none":
                article.column = ArticleColumn.objects.get(
                    id=request.POST["column"])
            else:
                article.column = None
            article.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误,请重新填写")
    else:
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {
            "article": article,
            "article_post_form": article_post_form,
            "columns": columns}
        return render(request, "article/update.html", context)
