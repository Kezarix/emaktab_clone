from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return None
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if not user.email:
            user.email = None
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm

    # Выводим роль в список, как у тебя на скрине
    list_display = ('username', 'email', 'last_name', 'first_name', 'role', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password', 'email', 'role', 'first_name', 'last_name'),
        }),
    )

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role', 'fathers_name', 'school_class', 'birth_date', 'parents')}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.email:
            obj.email = None
        super().save_model(request, obj, form, change)