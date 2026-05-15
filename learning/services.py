from .models import Resource


def recommend_course(skill, level, is_free):

    course = Resource.objects.filter(
        skill_id=skill,
        level=level,
        is_free=is_free
    ).order_by("-created_at").first()

    return course
