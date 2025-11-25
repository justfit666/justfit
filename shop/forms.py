# shop/forms.py
from django import forms
from .models import Expense, Product, ProductVariant

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'description']
