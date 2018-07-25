from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.db.models import Max
from django.core.files.storage import FileSystemStorage
from chartit import DataPool, Chart
# Create your views here.

from .models import Document, Flows, FlowTemplate

def template_upload_handler(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        
        # save file path to DB
        d = Document(path=uploaded_file_url, description=request.POST['description'])
        d.save()
        # save fps template
        d.upload_template()

        latest_flow_template = get_list_or_404(FlowTemplate)
        context = {'latest_flow_template': latest_flow_template}
        return render(request, 'poc/flowtemplate.html', context)
    else:
        return render(request, 'poc/upload_template.html')

def result_upload_handler(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        
        # save file path to DB
        d = Document(path=uploaded_file_url, description=request.POST['description'])
        d.save()
        # calculate result
        d.upload_result(request.POST['testcase'])
        return HttpResponseRedirect(reverse('poc:result'))
    else:
        latest_flow_set = Flows.objects.all().aggregate(Max('test_set'))
        return render(request, 'poc/upload_result.html', latest_flow_set)

def show_template(request):
    latest_flow_template = get_list_or_404(FlowTemplate)
    context = {'latest_flow_template': latest_flow_template}
    return render(request, 'poc/flowtemplate.html', context)

def show_result(request):
    try:
        latest_flow_set = Flows.objects.all().aggregate(Max('test_set'))['test_set__max']
        latest_flow = Flows.objects.filter(test_set=latest_flow_set)
        context = {'latest_flow': latest_flow, 'desc':"Latest Results", 'test_set':latest_flow_set}
        return render(request, 'poc/result.html', context)
    except Flows.DoesNotExist:
        return render(request, 'poc/result.html')

def show_stat(request):
    return render(request, 'poc/home.html')

def show_summary(request, test_set):
    return render(request, 'poc/home.html')


def chart_view(request, flow_id):
    flow_name = get_object_or_404(Flows, id=flow_id).flow_name

    #From Chartit.
    #Step 1: Create a DataPool with the data we want to retrieve.
    chartdata = DataPool(
        series=
        [
            {
             'options': { 'source': Flows.objects.filter(flow_name=flow_name).order_by('-pub_date')[:100] },
             'terms': ['pub_date','drop_time']
             }
        ]
    )
    #Step 2: Create the Chart object
    cht = Chart(
        datasource = chartdata,
        series_options =
            [{'options':{
                'type': 'line',
                'stacking': False
              },
              'terms':{
                'pub_date': ['drop_time']
              }
            }],
        chart_options =
        {
            'chart': {'backgroundColor': '#f2f2f2'},
            'title': {'text': 'Flow: '+flow_name},
            'yAxis': {'title' : {'text': 'Drop Time (ms)' }},
        }
    )

    #Step 3: Send the chart object to the template.
    return render(request,'poc/chart.html', {'chart': cht})