from data_module.models import *
from django import forms


class AnalysisForm(forms.Form):
    calculation_keys = forms.CharField(widget=forms.HiddenInput(attrs={
        'id': 'headerSelector'
    }))
    label_keys = forms.CharField(widget=forms.HiddenInput(attrs={
        'id': 'labels'
    }))
    analyser = forms.CharField(widget=forms.HiddenInput(attrs={
        'id': 'analyser'
    }))
    params = forms.CharField(widget=forms.HiddenInput(attrs={
        'id': 'params'
    }))
