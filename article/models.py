from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFit


class ArticleColumn(models.Model):
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    # 创建时间
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    # 文章作者
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章标题
    title = models.CharField(max_length=100)
    # 文章正文
    body = models.TextField()
    # 文章创建时间
    created = models.DateTimeField(default=timezone.now)
    # 文章更新时间
    updated = models.DateTimeField(auto_now=True)
    # 浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 文章标题图
    avatar = models.ImageField(upload_to="article/%Y%m%d/", blank=True)

    # 文章标签
    tags = TaggableManager(blank=True)

    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="article"
    )

    # 内部类用于给model定义元数据
    class Meta:
        # -created表明数据应该倒序排列
        ordering = ('-created',)

        def __str__(self):
            return self.title

    def get_absolute_url(self):
        return reverse("article:article_detail", args=[self.id])

    def save(self, *args, **kwargs):
        article = super(ArticlePost, self).save(*args, **kwargs)

        if self.avatar and not kwargs.get("update_fields"):
            avatar = ProcessedImageField(
                upload_to="article/%Y%m%d",
                processors=[ResizeToFit(width=400)],
                format="JPEG",
                options={"quantity": 100},
            )

        # if self.avatar and not kwargs.get("update_fields"):
        #     image = Image.open(self.avatar)
        #     (x, y) = image.size
        #     new_x = 400
        #     new_y = int(new_x * (y / x))
        #     resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
        #     resized_image.save(self.avatar.path)

        return article
