from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# Create your views here.

from .models import Document, Flows, FlowTemplate

def home(request):
    return render(request, 'poc/home.html')

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

        latest_flow = get_list_or_404(Flows, test_set=request.POST['testcase'])
        context = {'latest_flow': latest_flow, 'desc' : request.POST['description']}
        return render(request, 'poc/result.html', context)
    else:
        return render(request, 'poc/upload_result.html')

def show_template(request):
    latest_flow_template = get_list_or_404(FlowTemplate)
    context = {'latest_flow_template': latest_flow_template}
    return render(request, 'poc/flowtemplate.html', context)

def show_result(request):
    latest_flow = get_list_or_404(Flows)
    context = {'latest_flow': latest_flow, 'desc':"ALL Results"}
    return render(request, 'poc/result.html', context)

def show_stat(request):
    return render(request, 'poc/home.html')