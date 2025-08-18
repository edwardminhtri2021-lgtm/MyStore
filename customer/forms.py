from django import forms
from . import models

class FormCustumer(forms.ModelForm):
    username = forms.CharField(max_length=50, widget=forms.TextInput())
    password = forms.CharField(max_length=150, widget=forms.PasswordInput())
    confirm = forms.CharField(max_length=150, label='confirm', widget=forms.PasswordInput())
    fullname = forms.CharField(max_length=500, widget=forms.TextInput())
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'pattern': '((\([0-9]{3}\)[0-9]{9,15})|([0-9]{10,15}))', 'title': 'Your phone number must be (xxx)xxxxxxxxx or 0xxxxxxxxx'}))
    email = forms.EmailField(widget=forms.TextInput())
    address = forms.CharField(max_length=500, widget=forms.TextInput())

    class Meta:
        model = models.Customer
        fields = '__all__'

class FormDonHang(forms.ModelForm):
    ngaydathang = forms.DateField(widget=forms.TextInput())
    httt = forms.CharField(max_length=150, widget=forms.TextInput())
    diachigiaohang = forms.CharField(max_length=150, widget=forms.TextInput())
    tongtien = forms.FloatField(widget=forms.TextInput())
    tamung = forms.FloatField(widget=forms.TextInput())
    conlai = forms.FloatField(widget=forms.TextInput())

    class Meta:
        model = models.DonHang
        fields = '__all__'