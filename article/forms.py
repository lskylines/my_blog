from django import forms
from .models import ArticlePost

class ArticlePostForm(forms.ModelForm):
    class Meta:
        #指明数据模型来源
        model = ArticlePost
        #定义表单包含字段
        fields = ("title", "body")

