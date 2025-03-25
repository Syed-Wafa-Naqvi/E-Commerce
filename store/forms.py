from django import forms

class CheckoutForm(forms.Form):
    address = forms.CharField(label="Address", max_length=255)
    phone = forms.CharField(label="Phone", max_length=20)