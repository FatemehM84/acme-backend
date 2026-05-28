# account/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# ایمپورت مدل UserCourse از اپلیکیشن شما
# جای 'your_app_name' نام دقیق اپلیکیشن خود را بنویسید
from learning.models import UserCourse 

User = get_user_model()

# اینلاین برای نمایش دوره‌ها در پنل کاربر
class UserCourseInline(admin.TabularInline):
    model = UserCourse
    extra = 0  # 0 بگذارید تا شلوغ نشود
    fields = ("course", "status", "current_step", "started_at")
    readonly_fields = ("started_at",)
    autocomplete_fields = ("course",) # اگر می‌خواهید سرچ کنید

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserCourseInline]
    # سایر تنظیمات پیش‌فرض یوزر ادمین هم حفظ می‌شود
    list_display = BaseUserAdmin.list_display + ('email',)
