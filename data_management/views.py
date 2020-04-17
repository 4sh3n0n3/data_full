from django.shortcuts import render
from django.views import View
from .forms import *
from .utils import *
from django.db import transaction
from data_module.mongo_scripts import count_data, find_data

# Create your views here.
from django.views.generic import DetailView, ListView, CreateView, FormView


class ResearchGroupsList(ListView):
    model = ResearchGroup
    template_name = 'data_control/researches.html'
    context_object_name = 'research_groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_researches_menu_context())
        return context


class ResearchDetailView(DetailView):
    model = Research
    template_name = 'data_control/research_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_researches_menu_context())
        datasets = Dataset.objects.filter(researches=self.kwargs['pk'])
        for dataset in datasets:
            dataset.entries = find_data(dataset.name, limit=18)
            dataset.headers = Header.objects.filter(dataset=dataset).order_by('id')
        context.update({'related_datasets': datasets})
        return context


class CreateDatasetView(CreateView):
    model = Dataset
    form_class = DatasetCreateForm
    template_name = 'data_control/dataset_create.html'

    def get_success_url(self):
        return '/data_manage/dataset/upload/{}'.format(self.kwargs['pk'])


class CreateResearchView(CreateView):
    model = Research
    form_class = ResearchCreateForm
    main_page_template = 'data_control/researches.html'
    template_name = 'data_control/research_create.html'

    def get_main_page_context(self, **kwargs):
        context = get_researches_menu_context()
        return context

    def get_success_url(self):
        return '/data_manage/researches/'


class UploadDataToDatasetView(FormView):
    form_class = DatasetDataUploadForm
    template_name = 'data_control/dataset_upload.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dataset'] = Dataset.objects.get(id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        with transaction.atomic():
            upload_data_to_dataset(file=form.cleaned_data['file'], file_type=form.cleaned_data['file_format'],
                                   dataset=Dataset.objects.get(id=self.kwargs['pk']))
        return super().form_valid(form)

    def get_success_url(self):
        return '/data_manage/dataset/set_header_types/{}'.format(self.kwargs['pk'])


class SetHeaderTypesView(View):
    template_name = 'data_control/dataset_header_types.html'
    main_page_template = 'data_control/researches.html'
    showed_rows_count = 18
    header_prefix = 'header_'

    def get_main_page_context(self, **kwargs):
        context = get_researches_menu_context()
        return context

    def collect_form_context(self):
        dataset = Dataset.objects.get(id=self.kwargs['pk'])
        context = {
            'headers': Header.objects.filter(dataset=dataset).order_by('id'),
            'dataset': dataset,
            'first_rows': find_data(dataset.name, limit=self.showed_rows_count),
            'custom_types': CustomType.objects.all(),
            'showed_rows': self.showed_rows_count,
            'n_rows': count_data(dataset.name)
        }
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.collect_form_context())

    def post(self, request, *args, **kwargs):
        if 'return' in request.POST:
            return render(request, self.main_page_template, self.get_main_page_context())

        with transaction.atomic():
            for data in request.POST:
                if data.startswith(self.header_prefix):
                    header_id = int(data[len(self.header_prefix):])
                    custom_type_id = int(request.POST[data])
                    header = Header.objects.get(id=header_id)
                    if header.custom_type.id != custom_type_id:
                        print('howdy')
                        new_custom_type = CustomType.objects.get(id=custom_type_id)
                        header.custom_type = new_custom_type
                        header.save()

        if 'change_data' in request.POST:
            context = self.collect_form_context()
            context.update({'success_message': 'Данные успешно обновлены'})
            return render(request, self.template_name, context)

