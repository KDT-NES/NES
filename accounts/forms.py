from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from django import forms


class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = (
            "username",
            "email",
            "nickname",
            "location",
            "location_detail",
        )
        labels = {
            "username": "아이디",
            "email": "이메일",
            "nickname": "이름",
            "location": "주소",
            "location_detail": "상세주소",
        }


class UpdateForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = (
            "creater_name",
            "email",
            "location",
            "location_detail",
        )


class UpdateDetailForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = (
            "creater_name",
            "profileimage",
            "introduce",
            "email",
            "location",
            "location_detail",
        )


class UpdateSocialForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = (
            "facebook",
            "github",
            "instagram",
        )
