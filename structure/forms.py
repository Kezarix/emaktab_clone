# structure/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()

class eMaktabLoginForm(AuthenticationForm):
    username = forms.CharField(label="Login")
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)


class eMaktabRegisterForm(forms.ModelForm):
    password = forms.CharField(label="Parol", widget=forms.PasswordInput)
    password_confirm = forms.CharField(label="Parolni tasdiqlang", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'fathers_name', 'email', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError("Parollar bir-biriga mos kelmadi.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'parent'
        if commit:
            user.save()
        return user