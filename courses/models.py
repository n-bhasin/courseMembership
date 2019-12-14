from django.db import models
from django.urls import reverse
from myapp.models import Membership


# Create your models here.

class Course(models.Model):
	slug = models.SlugField()
	title = models.CharField(max_length=40)
	description = models.TextField()
	allowed_membership = models.ManyToManyField(Membership)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('courses:detail', kwargs={'slug': self.slug})

	@property
	def lessons(self):
		return self.lessons_set.all().order_by(
			'position')  # syntax for foreign key object grab all the lessons associated with it.


class Lessons(models.Model):
	slug = models.SlugField()
	title = models.CharField(max_length=40)
	course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
	position = models.IntegerField()
	video_url = models.CharField(max_length=250)
	thumbnail = models.ImageField()

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('courses:lesson_detail',
		               kwargs={'course_slug': self.course.slug, 'lesson_slug': self.slug})
