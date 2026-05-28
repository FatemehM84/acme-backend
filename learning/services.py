from .models import Resource

def recommend_course(skill, subskill, level, is_free, duration_minutes, resource_type):
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
    
    course = Resource.objects.filter(
        skill_id=skill,
        subskill_id=subskill,
        level=level,
        is_free=is_free,
        duration_minutes=duration_minutes,
    ).order_by("-created_at").first()
    
    return course
