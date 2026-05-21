from .models import Resource


def recommend_course(skill, level, is_free, duration_minutes, Resource_types):

    course = Resource.objects.filter(
        skill_id=skill,
        level=level,
        is_free=is_free,
        duration_minutes=duration_minutes,
        Resource_types=Resource_types
    ).order_by("-created_at").first()

    if course:
        return course
    
    course = Resource.objects.filter(
        skill_id=skill,
        level=level,
        is_free=is_free,
        duration_minutes=('medium' , 'متوسط'),
        Resource_types=Resource_types
    ).order_by("-created_at").first()

    if course:
        return course
    
    
    return course
