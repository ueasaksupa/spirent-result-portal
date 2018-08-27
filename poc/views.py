from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.db.models import Max
from django.db.models import Q

from django.core.files.storage import FileSystemStorage
from chartit import DataPool, Chart
# Create your views here.

from .models import Document, Flows, FlowTemplate, FlowSummary

def template_upload_handler(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        doctype = request.POST['doctype']
        
        # save file path to DB
        d = Document(path=uploaded_file_url, description=request.POST['description'])
        d.save()
        # save fps template
        d.upload_template(doctype=doctype)

        return HttpResponseRedirect(reverse('poc:showtemplate'))
    else:
        return render(request, 'poc/upload_template.html')

def result_upload_handler(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        doctype = request.POST['doctype']
        description = 'no description' if request.POST['description'] == '' else request.POST['description']
        # save file path to DB
        data = Document(path=uploaded_file_url, description=description, test_set=request.POST['testcase'])
        data.save()
        # calculate result
        if request.POST['service_type'] == 'other':
            try:
                data.save_other_service_result(request.POST['testcase'], doctype)
            except:
                return render(request, 'poc/error.html')
        else:
            try:
                data.save_multicast_service_result(request.POST['testcase'], request.POST['service_type'], doctype)
            except:
                return render(request, 'poc/error.html')
        return HttpResponseRedirect(reverse('poc:resultdetail', args=(request.POST['testcase'],)))
    else:
        latest_flow_set = Document.objects.all().aggregate(Max('test_set'))
        return render(request, 'poc/upload_result.html', latest_flow_set)    

def show_template(request):
    try:
        latest_flow_template = FlowTemplate.objects.all()
        context = {'latest_flow_template': latest_flow_template}
        return render(request, 'poc/flowtemplate.html', context)
    except FlowTemplate.DoesNotExist:
        return render(request, 'poc/flowtemplate.html')

def show_result(request,test_set):
    try:
        queried_flow = Flows.objects.filter(test_set=test_set)
        latest_flow = []
        for row in queried_flow:
            latest_flow.append( {'flow_name':row.flow_name, 'tx':row.tx, 'rx':row.rx, 'drop_count':row.drop_count, 'drop_time':row.drop_time, 'id':row.id,
                                 'test_set':row.test_set, 'service_type':row.service_type, 'bg_service':row.bg_service, 'fps':row.fps,
                                 'drop_percent':'N/A' if row.rx <= 0 else round((row.drop_count/row.tx)*100,5)} )
        try:
            desc = Document.objects.filter( ~Q(description='') , test_set=test_set )[0].description
            context = {'latest_flow': latest_flow, 'desc':desc, 'test_set':test_set}
        except IndexError:
            context = {'latest_flow': latest_flow, 'desc':'no description', 'test_set':test_set}
        return render(request, 'poc/result_detail.html', context)
    except Flows.DoesNotExist:
        return render(request, 'poc/result_detail.html')

def show_all_results(request):
    try:
        uniq_set = {}
        uniq_list = []
        alltestcases = Document.objects.order_by('test_set').values('test_set','description','remark','uploaded_at').distinct()
        for case in alltestcases:
            if case['test_set'] not in uniq_set:
                uniq_list.append( {'test_set':case['test_set'], 'description':case['description'], 'remark':case['remark'], 'uploaded_at':case['uploaded_at'] } )
                uniq_set[case['test_set']] = True
            else:
                if case['description'].strip() not in uniq_list[-1]['description'].strip():
                    uniq_list[-1]['description'] += ' :: '+case['description'].strip()
                if len(uniq_list[-1]['description']) > 60:
                    uniq_list[-1]['description'] = uniq_list[-1]['description'][:60] + ' ...'

        context = {'alltestcases': uniq_list , 'desc':"All Testcases Results"}
        return render(request, 'poc/results.html', context)
    except Flows.DoesNotExist:
        return render(request, 'poc/results.html')

# def show_stat(request):
#     return render(request, 'poc/home.html')

def show_summary(request, test_set):
    try:
        summary_flow = FlowSummary.objects.filter(test_set=test_set)
        try:
            desc = Document.objects.filter( ~Q(description='') , test_set=test_set )[0].description
            context = {'summary_flow': summary_flow, 'desc':"Summary result for: "+desc, 'test_set':test_set}
        except IndexError:
            context = {'latest_flow': latest_flow, 'desc':'no description', 'test_set':test_set}
        return render(request, 'poc/summary.html', context)
    except Flows.DoesNotExist:
        return render(request, 'poc/summary.html')

def edit_remark(request):
    if request.method == 'POST':
        test_set = request.POST['test_set']
        remark = request.POST['remark']
        
        print (test_set, remark)
        doc = Document.objects.filter(test_set=test_set)
        for record in doc:
            record.remark = remark
            record.save()
        return HttpResponseRedirect(reverse('poc:result'))

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