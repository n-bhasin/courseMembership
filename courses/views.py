from django.shortcuts import render
from django.views.generic import ListView, DetailView, View

from myapp.models import UserMembership
from .models import Course, Lessons


# Create your views here.

class CourseListView(ListView):
	model = Course


class CourseDetailView(DetailView):
	model = Course


class LessonDetailView(View):

	def get(self, request, course_slug, lesson_slug, *args, **kwargs):
		context = {}
		course_qs = Course.objects.filter(slug=course_slug)

		if course_qs.exists():
			course = course_qs.first()

		lesson_qs = course.lessons.filter(slug=lesson_slug)

		if lesson_qs.exists():
			lesson = lesson_qs.first()

		user_membership = UserMembership.objects.filter(user=request.user).first()
		user_membership_type = user_membership.membership.membership_type
		courses_allowed_mem_type = course.allowed_membership.all()

		print('user_membership_type', user_membership_type)
		print('courses_allowed_mem_type', courses_allowed_mem_type)

		context['lesson'] = None
		if courses_allowed_mem_type.filter(membership_type=user_membership_type).exists():
			print('courses_allowed_mem_type', courses_allowed_mem_type)
			context['lesson'] = lesson
		return render(request, 'courses/lesson_detail.html', context)
