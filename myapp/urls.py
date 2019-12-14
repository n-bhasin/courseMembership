from django.urls import path
from .views import MembershipSelectView, paymentView, update_transactions, profile, cancel_subscription

app_name = 'myapp'

urlpatterns = [
	path('', MembershipSelectView.as_view(), name='select'),
	path('payment/', paymentView, name='payment'),
	path('update-transactions/<subscription_id>/', update_transactions, name='update-transactions'),
	path('profile/', profile, name='profile'),
	path('cancel_subscription/', cancel_subscription, name='cancel_subscription'),
]
