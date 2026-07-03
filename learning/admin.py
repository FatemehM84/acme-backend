from django.contrib import admin
from .models import Skill, Resource, ResourceStep, UserCourse
from django.utils.html import format_html
from .models import Skill, SubSkill


class ResourceStepInline(admin.TabularInline):
    model = ResourceStep
    extra = 1 
    fields = ('title', 'order', 'duration_minutes') 

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    inlines = [ResourceStepInline]

    list_display = (
        "id",
        "title",
        "skill",
        "subskill",
        "resource_type",
        "level",
        "is_free",
        "duration_minutes",
        "image_preview",
    )

    list_display_links = (
        "id",
        "title",
    )

    list_filter = (
        "skill",
        "subskill",
        "level",
        "resource_type",
        "is_free",
        "duration_minutes",
        "language",
    )

    search_fields = (
        "title",
        "description",
        "provider_name",
        "url",
        "skill__name",
        "subskill__name",
    )

    fields = (
        "skill",
        "subskill",
        "title",
        "resource_type",
        "description",
        "image",
        "image_preview",
        "provider_name",
        "url",
        "language",
        "level",
        "is_free",
        "duration_minutes",
    )

    readonly_fields = (
        "image_preview",
    )

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:60px;width:90px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "Preview"



@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'started_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'course__title')



class SubSkillInline(admin.TabularInline):
    model = SubSkill
    extra = 1
    fields = ("name", "image", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        
        if obj and obj.image:
            return format_html('<img src="{}" style="height:40px;border-radius:6px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Preview"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "image_preview")
    list_display_links = ("id","name",)
    search_fields = ("name", "category")
    inlines = [SubSkillInline]
    fields = ("name", "slug", "description", "category", "image", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:8px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Preview"


@admin.register(SubSkill)
class SubSkillAdmin(admin.ModelAdmin):
    list_display = ("id", "skill", "name", "image_preview")
    list_display_links = ("id","name",)
    list_filter = ("skill",)
    search_fields = ("name", "skill__name")
    fields = ("skill", "name", "image", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:8px;" />', obj.image.url)
        return "—"
    image_preview.short_description = "Preview"
