from django.contrib import admin
from fourlabs_auth.models import User, EmailLoginCode, UserToken, TokenUsageLog
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_superuser']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {'fields': ('first_name', 'last_name')}),
        (_('Permissões'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Datas Importantes'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(EmailLoginCode)
class EmailLoginCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'created_at', 'is_valid_display')
    search_fields = ('email', 'code')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    def is_valid_display(self, obj):
        return obj.is_valid()
    is_valid_display.boolean = True
    is_valid_display.short_description = 'Código válido?'


@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "tokens_restantes",
        "total_tokens_diarios",
        "last_reset",
    )
    list_filter = ("last_reset",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    ordering = ("-last_reset",)
    readonly_fields = ("last_reset",)

    fieldsets = (
        (None, {
            "fields": ("user", "tokens_restantes", "total_tokens_diarios", "last_reset")
        }),
    )


@admin.register(TokenUsageLog)
class TokenUsageLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "quantidade",
        "tokens_restantes",
        "created_at",
    )
    list_filter = ("action", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name")
    ordering = ("-created_at",)
    readonly_fields = ("user", "action", "quantidade", "tokens_restantes", "created_at")

    fieldsets = (
        (None, {
            "fields": ("user", "action", "quantidade", "tokens_restantes", "created_at")
        }),
    )
