from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class CustomUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Email")

    class Meta:
        model = User
        fields = (
            'username', 'password', 'email', 'role',
            'first_name', 'last_name', 'fathers_name',
            'phone', 'major', 'school_class',
        )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email or None

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        major = cleaned.get('major')

        # учитель обязан иметь major
        if role == 'teacher' and not major:
            self.add_error('major', 'Major is required for teachers.')
        return cleaned

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

    list_display = (
        'username', 'email', 'last_name', 'first_name',
        'role', 'major', 'is_staff',
    )
    list_filter = ('role', 'is_staff', 'is_active', 'major')
    search_fields = ('username', 'first_name', 'last_name', 'email')

    # -------- форма СОЗДАНИЯ --------
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password',
                'email', 'role',
                'first_name', 'last_name', 'fathers_name',
                'phone', 'major', 'school_class',
            ),
        }),
    )

    # -------- форма РЕДАКТИРОВАНИЯ --------
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': (
                'role', 'fathers_name', 'phone',
                'major', 'school_class',
                'birth_date', 'parents',
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.email:
            obj.email = None
        super().save_model(request, obj, form, change)