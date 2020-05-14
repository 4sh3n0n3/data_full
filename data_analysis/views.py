from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.db import transaction
from data_module.mongo_scripts import count_data, find_data
from .utils import *
from data_prod.settings import *
from .forms import AnalysisForm

# Create your views here.
from django.views.generic import DetailView, ListView, CreateView, FormView, RedirectView


class ResearchListView(ListView):
    model = ResearchGroup
    template_name = 'data_analysis/researches.html'
    context_object_name = 'research_groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_researches_menu_context())
        return context


class DatasetListView(ListView):
    model = Dataset
    template_name = 'data_analysis/datasets.html'
    context_object_name = 'datasets'
    n_rows = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_datasets_by_research_id(self.kwargs['pk'], n_rows=self.n_rows))
        context.update(get_researches_menu_context())
        context.update({'n_rows': self.n_rows})
        return context


# class DatasetDetailView(DetailView):
#     model = Dataset
#     template_name = 'data_analysis/dataset_details.html'
#
#     def get_context_data(self, **kwargs):
#         dataset = Dataset.objects.get(id=self.kwargs['pk'])
#         context = super().get_context_data(**kwargs)
#         context.update(add_dataset_details(dataset, n_rows=18))
#         context.update({'analysers': ANALYSERS})
#         context.update({'form': AnalysisForm()})
#         return context


class PreVisualisationRedirectView(RedirectView):
    init_context = {}
    template = ''
    url = '/pre_visualise/'

    def get(self, request, *args, **kwargs):
        print(self.init_context)
        print(self.template)
        return render(request, self.template, self.init_context)


class AnalyseData(View):
    form_class = AnalysisForm
    template_name = 'data_analysis/dataset_details.html'

    def get_context(self):
        dataset = Dataset.objects.get(id=self.kwargs['pk'])
        context = {
            'analysers': ANALYSERS,
            'form': AnalysisForm(),
            'dataset': dataset,
        }
        context.update(add_dataset_details(dataset, n_rows=18))
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            dataset = Dataset.objects.get(id=self.kwargs['pk'])

            headers_projection = {value: True for value in eval(request.POST['calculation_keys']).values() if value != ''}
            labels = {value: True for value in eval(request.POST['label_keys']).values() if value != ''}
            analyser = ANALYSERS.get(eval(request.POST['analyser']).get('method'))
            params = eval(request.POST['params'])

            result, template_context, labels = analyse(dataset, analyser, labels, projection=headers_projection, params=params)

            context = {
                'result': result,
                'template_context': template_context,
                'labels': labels,
            }
            template = 'pre_visual_info_blocks/' + analyser.get('pre_visualisation_template')

            return PreVisualisationRedirectView.as_view(init_context=context, template=template)(request)

        return render(request, self.template_name, self.get_context())
