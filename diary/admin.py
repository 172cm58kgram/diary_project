from django.contrib import admin
from .models import DiaryEntry, Tag, AccessLog  # Tagもimport

# DiaryEntryを管理画面で表示できるように設定
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date')  # 一覧画面で表示するフィールド
    search_fields = ('title', 'content', 'user__email')  # 検索可能なフィールド
    list_filter = ('date', 'tags')  # フィルタ可能なフィールド
    filter_horizontal = ('tags',)  # 🔹 多対多フィールドを管理画面で使いやすくする

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "ip_address", "user_email", "user_username", "user_agent", "referer")
    search_fields = ("ip_address", "user__email", "user__username", "user_agent", "referer")
    list_filter = ("timestamp",)

    def user_email(self, obj):
        return obj.user.email if obj.user else "ゲスト"
    user_email.short_description = "ユーザーメール"

    def user_username(self, obj):
        return obj.user.username if obj.user else "ゲスト"
    user_username.short_description = "ユーザーネーム"

# Tagモデルも管理画面に登録
admin.site.register(Tag)
admin.site.register(DiaryEntry, DiaryEntryAdmin)