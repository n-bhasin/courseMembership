from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.urls import reverse

from .models import Membership, UserMembership, Subscription

import stripe


# Create your views here.
def profile(request):
	context = {}
	user_membership = get_user_membership(request)
	selected_membership = get_selected_membership(request)

	context['user_membership']: user_membership
	context['selected_membership']: selected_membership

	return render(request, '../templates/myapp/profile.html', context)


def get_user_membership(request):
	user_membership_qs = UserMembership.objects.filter(user=request.user)
	if user_membership_qs.exists():
		return user_membership_qs.first()
	return None


def get_user_subscription(request):
	user_subscription = Subscription.objects.filter(user_membership=get_user_membership(request))
	if user_subscription.exists():
		return user_subscription
	return None


def get_selected_membership(request):
	membership_type = request.session['selected_membership']
	selected_membership_type_qs = Membership.objects.filter(membership_type=membership_type)
	if selected_membership_type_qs.exists():
		return selected_membership_type_qs.first()
	return None


class MembershipSelectView(ListView):
	model = Membership

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(**kwargs)
		current_membership = get_user_membership(self.request)
		context['current_membership'] = str(current_membership.membership)
		return context

	def post(self, request, **kwargs):
		selected_membership_type = request.POST.get('membership_type')

		user_membership = get_user_membership(request)
		user_subscription = get_user_subscription(request)

		selected_membership_qs = Membership.objects.filter(membership_type=selected_membership_type)

		if selected_membership_qs.exists():
			selected_membership = selected_membership_qs.first()

		'''
		======
		VALIDATION
		======
		'''
		if user_membership == selected_membership:
			if user_subscription is not None:
				messages.info(request, 'You already subscribed ot this membership. Your payment is due on {}'.format(
					'get value from stripe'))
				return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

		# assign to session
		request.session['selected_membership'] = selected_membership.membership_type

		return HttpResponseRedirect(reverse('myapp:payment'))


def paymentView(request):
	user_membership = get_user_membership(request)
	print('membership', user_membership.stripe_customer_id)

	selected_membership = get_selected_membership(request)
	print('PLAN', selected_membership.stripe_plan_id)
	publish_key = settings.STRIPE_PUBLISHABLE_KEY

	if request.method == 'POST':
		print(request.method)

		try:
			token = request.POST['stripeToken']
			print(token)

			source_var = stripe.Source.modify(token,
			    metadata={"plan": selected_membership.stripe_plan_id}, )
			print(source_var)

			subscription = stripe.Subscription.create(
				customer=user_membership.stripe_customer_id,
				items=[{'plan': selected_membership.stripe_plan_id, }],

			)

			return redirect(reverse('myapp:update-transactions',
			                        kwargs={
				                        'subscription_id': subscription.id
			                        }))

		except stripe.error.InvalidRequestError as e:
			print(stripe.Card)
			print('error: ', e)
			print('Status is: %s' % e.http_status)
			print('Type is: %s' % e.error.type)
			print('Code is: %s' % e.error.code)
			# param is '' in this case
			print('Param is: %s' % e.error.param)
			print('Message is: %s' % e.error.message)
			messages.info(request, 'Your card has been declined.')


	context = {
		'publishKey': publish_key,
		'selected_membership': selected_membership
	}

	return render(request, 'myapp/membership_payment.html', context)


def update_transactions(request, subscription_id):
	user_membership = get_user_membership(request)
	selected_membership = get_selected_membership(request)

	user_membership.membership = selected_membership
	user_membership.save()

	sub, created = Subscription.objects.get_or_create(user_membership=user_membership)
	sub.stripe_subscription_id = subscription_id
	sub.active = True
	sub.save()

	try:
		del request.session['selected_membership']
	except:
		pass
	messages.info(request, 'Successfully created {} membership'.format(selected_membership))
	return redirect('/courses')


def cancel_subscription(request):
	user_sub = get_user_subscription(request)

	if user_sub.active is not True:
		messages.info(request, "You don't have an active subscription.")
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
	sub.delete()

	user_sub.active = False
	user_sub.save()

	free_membership = Membership.objects.filter(membership_type='Free').first()
	user_membership = get_user_membership(request)
	user_membership.membership = free_membership
	user_membership.save()

	messages.info(request, 'Successfully canceled subscription.')

	return redirect('/myapp')
