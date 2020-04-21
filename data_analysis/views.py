from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.db import transaction
from data_module.mongo_scripts import count_data, find_data
from .utils import *
from data_prod.settings import *
from .forms import AnalysisForm

# Create your views here.
from django.views.generic import DetailView, ListView, CreateView, FormView


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


class AnalyseData(View):
    form_class = AnalysisForm
    template_name = 'data_analysis/dataset_details.html'

    def get_context(self):
        dataset = Dataset.objects.get(id=self.kwargs['pk'])
        context = {}
        context.update(add_dataset_details(dataset, n_rows=18))
        context.update({'analysers': ANALYSERS})
        context.update({'form': AnalysisForm()})
        context.update({'dataset': dataset})
        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            dataset = Dataset.objects.get(id=self.kwargs['pk'])

            headers_projection = {value: True for value in eval(request.POST['calculation_keys']).values()}
            labels = {value: True for value in eval(request.POST['label_keys']).values()}
            analyser = ANALYSERS.get(eval(request.POST['analyser']).get('method'))
            params = eval(request.POST['params'])

            result = analyse(dataset, analyser, labels, projection=headers_projection, params=params)
            return HttpResponseRedirect('/success/')

        return render(request, self.template_name, self.get_context())
