from django.db import models

# Create your models here.
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


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

    image = models.ImageField(
        upload_to="skills/",
        blank=True,
        null=True
    )

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
    


class SubSkill(models.Model):
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="subskills"
    )
    name = models.CharField(
        max_length=255
    )
    slug = models.SlugField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)


    image = models.ImageField(
        upload_to="subskills/",
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ("skill", "name")
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.skill.name} -> {self.name}"
    



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

    subskill = models.ForeignKey(
        SubSkill,
        on_delete=models.PROTECT,
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

    image = models.ImageField(
        upload_to="courses/",
        blank=True,
        null=True
    )

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
        related_name="user_courses",
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
        blank=True,
        related_name="current_for_user_courses"
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

    def update_progress_state(self):
        course_steps = self.course.steps.order_by("order")
        total_steps = course_steps.count()

        if total_steps == 0:
            self.current_step = None
            self.status = "active"
            self.completed_at = None
            self.save(update_fields=[
                "current_step",
                "status",
                "completed_at",
                "updated_at",
            ])
            return

        done_step_ids = set(
            self.step_progresses
            .filter(is_done=True)
            .values_list("step_id", flat=True)
        )

        first_not_done_step = (
            course_steps
            .exclude(id__in=done_step_ids)
            .first()
        )

        if first_not_done_step:
            self.current_step = first_not_done_step
            self.status = "active"
            self.completed_at = None
        else:
            self.current_step = None
            self.status = "completed"

            if not self.completed_at:
                self.completed_at = timezone.now()

        self.save(update_fields=[
            "current_step",
            "status",
            "completed_at",
            "updated_at",
        ])

    def __str__(self):
        return f"{self.user} - {self.course.title}"


class UserCourseStepProgress(models.Model):
    user_course = models.ForeignKey(
        UserCourse,
        on_delete=models.CASCADE,
        related_name="step_progresses"
    )
    step = models.ForeignKey(
        ResourceStep,
        on_delete=models.CASCADE,
        related_name="user_progresses"
    )
    is_done = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user_course", "step")
        ordering = ["step__order"]

    def clean(self):
        if self.user_course_id and self.step_id:
            if self.step.resource_id != self.user_course.course_id:
                raise ValidationError(
                    "This step does not belong to the selected user course."
                )

    def save(self, *args, **kwargs):
        self.clean()

        if self.is_done and not self.completed_at:
            self.completed_at = timezone.now()

        if not self.is_done:
            self.completed_at = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_course} - {self.step} - done={self.is_done}"




class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Profile of {self.user}"


# ایجاد خودکار پروفایل بلافاصله پس از ایجاد کاربر جدید
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)