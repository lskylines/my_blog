from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ArticlePost
from .forms import ArticlePostForm
from django.contrib.auth.models import User
import markdown

def article_list(request):
    articles = ArticlePost.objects.all()
    context = {"articles": articles}
    return render(request, "article/list.html", context)


def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)

    #将Markdown语法渲染成HTML
    article.body = markdown.markdown(article.body,
    extensions=[
        #包含缩写，表格等常用扩展
        'markdown.extensions.extra',
        #语法高亮扩展
        #'markdown.extensions.codehilite',
    ])
    context = {"article": article}
    return render(request, "article/detail.html", context)

def article_create(request):
    if request.method == "POST":
        print("article create post....")
        article_post_form = ArticlePostForm(data=request.POST)
        #判断提交数据是否满足模型
        if article_post_form.is_valid():
            #保存数据，暂不提交到数据库
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=1)
            new_article.save()

            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，重新填写")
    else:
        article_post_form = ArticlePostForm()
        context = {"article_post_form": article_post_form}
        return render(request, "article/create.html", context)


def article_delete(request, id):
    article = ArticlePost.objects.get(id = id)
    article.delete()
    return redirect("article:article_list")


def article_safe_delete(request, id):
    if request.method == "POST":
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


def article_update(request, id):
    article = ArticlePost.objects.get(id=id)
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