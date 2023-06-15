from django.db import models
from django.contrib.auth.models import User
#引入内置信号
from django.db.models.signals import post_save
#引入信号接收器的装饰器
from django.dispatch import receiver



