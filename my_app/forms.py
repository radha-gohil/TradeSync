from django import forms
from .models import UserProfile, Portfolio,TrendingStock


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']
        

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['stock_symbol', 'quantity', 'purchase_price', 'purchase_date']
