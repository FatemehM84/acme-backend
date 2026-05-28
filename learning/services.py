from .models import Resource

def recommend_course(skill, subskill, level, is_free, duration_minutes, resource_type):
    # ۱. جستجوی کاملاً دقیق با استفاده از تمام پارامترها از جمله ریزمهارت (SubSkill)
    course = Resource.objects.filter(
        skill_id=skill,
        subskill_id=subskill,
        level=level,
        is_free=is_free,
        duration_minutes=duration_minutes,
        resource_type=resource_type
    ).order_by("-created_at").first()

    if course:
        return course
    
    # ۲. Fallback: اگر با پارامتر زمان پیدا نشد، جستجو بدون فیلتر کردن مدت زمان (duration_minutes)
    course = Resource.objects.filter(
        skill_id=skill,
        subskill_id=subskill,
        level=level,
        is_free=is_free,
        resource_type=resource_type
    ).order_by("-created_at").first()
    
    return course
