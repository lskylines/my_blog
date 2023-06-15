from django import forms
from django.contrib.auth.models import User


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()



class UserRegisterForm(forms.ModelForm):
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = User
        fields = ("username", "email")

    #对两次输入密码是否一致检查
    def clean_password2(self):

        data = self.cleaned_data
        user = User.objects.get(username=data["username"])
        print("校验密码是否相同", data.get("password"), data.get("password2"))
        if data.get("password") == data.get("password2"):
            return data.get("password")
        else:
            return forms.ValidationError("密码输入不一致，请重试")



