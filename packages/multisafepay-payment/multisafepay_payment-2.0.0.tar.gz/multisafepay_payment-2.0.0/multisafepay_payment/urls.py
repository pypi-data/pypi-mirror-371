from django.urls import path

from multisafepay_payment.views import MultisafePayPaymentView


urlpatterns = [
    path("", MultisafePayPaymentView.as_view(), name="multisafe-payment"),
]
