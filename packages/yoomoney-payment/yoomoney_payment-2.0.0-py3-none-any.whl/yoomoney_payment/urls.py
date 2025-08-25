from django.urls import path
from yoomoney_payment.views import YooMoneyPaymentView

urlpatterns = [
    path("", YooMoneyPaymentView.as_view(), name="yoomoney-payment"),
]
