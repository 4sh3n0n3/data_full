from data_module.models import *
from django import forms
from data_prod.settings import DATA_CONVERTERS


class DatasetCreateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        "id": "dataset_name_input",
        "class": "form-control",
    }))

    researches = forms.ModelMultipleChoiceField(
        queryset=Research.objects.all(),
        widget=forms.SelectMultiple(attrs={
            "id": "dataset_researches_input",
            "class": "form-control",
        }))

    owner = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={
            "id": "dataset_owner_input",
            "class": "form-control",
        })
    )

    class Meta:
        model = Dataset
        fields = ['name', 'researches', 'owner']

    def save_model(self, request, obj, form, change):
        user = request.user
        instance = form.save(commit=False)
        if not change or not instance.created_by:
            instance.created_by = user
        instance.save()
        form.save_m2m()
        return instance


class ResearchCreateForm(forms.ModelForm):
    research_name = forms.CharField(widget=forms.TextInput(attrs={
        "id": "research_name_input",
        "class": "form-control",
    }))

    group = forms.ModelChoiceField(
        required=False,
        queryset=ResearchGroup.objects.all(),
        widget=forms.Select(attrs={
            "id": "research_group",
            "class": "form-control",
        })
    )

    description = forms.CharField(widget=forms.Textarea(attrs={
        "id": "research_description",
        "class": "form-control",
    }))

    class Meta:
        model = Research
        fields = ['research_name', 'group', 'description']

    # def save_model(self, request, obj, form, change):
    #     user = request.user
    #     instance = form.save(commit=False)
    #     if not change or not instance.created_by:
    #         instance.created_by = user
    #     print(instance)
    #     instance.save()
    #     return instance


class DatasetDataUploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={
        "id": "loaded_file",
        "class": "custom-file-input",
    }))
    file_format = forms.ChoiceField(
        choices=[(v, k) for k, v in DATA_CONVERTERS.items()],
        widget=forms.Select(attrs={
            "id": "file_type",
            "class": "form-control"
        }))
