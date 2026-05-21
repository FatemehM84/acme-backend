from django.db import models

# Create your models here.
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone



class Skill(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True
    )

    slug = models.SlugField(
        unique=True,
        blank=True
    )

    description = models.TextField()

    category = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    



class Resource(models.Model):

    class LevelChoices(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    Resource_types = [
        ('video' , 'فیلم'),
        ('article' , 'مقاله'),
        ('course' , 'کورس'),
        ('podcast' , 'صوتی-پادکست'),
    ]

    Time_It_Takes = [
        ('short' , 'کوتاه'),
        ('medium' , 'متوسط'),
        ('long' , 'بلند مدت'),
        ('too long' , 'طولانی مدت'),
    ]

    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="resources"
    )

    title = models.CharField(
        max_length=255
    )

    resource_type = models.CharField(
        choices=Resource_types,
        max_length=20)

    description = models.TextField()

    provider_name = models.CharField(
        max_length=255
    )

    url = models.URLField()

    language = models.CharField(
        choices=[('Persian' , 'فارسی'),
                 ('English' , 'انگلیسی'),
                 ],
        max_length=20
    )

    level = models.CharField(
        max_length=20,
        choices=LevelChoices.choices
    )

    is_free = models.BooleanField(
        default=True
    )

    duration_minutes =models.CharField(
        max_length=20,
        choices=Time_It_Takes,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
    



class ResourceStep(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="steps"
    )

    title = models.CharField(
        max_length=255,
        blank=True
    )

    order = models.PositiveIntegerField()

    duration_minutes = models.PositiveIntegerField()  # مثلا 40، 60، ...

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["order"]
        unique_together = ("resource", "order")

    def __str__(self):
        return f"{self.resource.title} - Step {self.order} ({self.title or ''})"



class UserCourse(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_courses"
    )

    course = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name="user_courses"
    )


    current_step = models.ForeignKey(
        ResourceStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    started_at = models.DateTimeField(
        default=timezone.now
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("user", "course")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.course.title}"

