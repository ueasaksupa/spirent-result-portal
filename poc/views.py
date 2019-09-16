from django.shortcuts import render, get_object_or_404,get_list_or_404
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db.models import Max
from django.db.models import Q
from django.utils import timezone

from django.core.files.storage import FileSystemStorage
from chartit import DataPool, Chart
# Create your views here.
import re
from .models import testCase, testResult, testTry, testUpload, mcastFPS

def error_404_view(request, exception):
	return render(request,'poc/404.html')

def result_upload_handler(request):
	#####
	## for after upload result
	#####
	if request.method == 'POST' and request.POST['testresult']:
		testupload = testUpload(csv_result=request.POST['testresult'])
		testupload.save()
		try:
			tt = testTry.objects.get(test_no=request.POST['testno'])
			tt.result_process(request.POST['testresult'], request.POST['testno'], request.POST['testcase'], testupload.id)
			# return render(request, 'poc/upload_result.html')
			return HttpResponseRedirect(reverse('poc:resultdetail', args=(request.POST['testno'],)))
		except testTry.DoesNotExist:
			result = testTry(test_no=request.POST['testno'], testcase_id=request.POST['testcase'])
			result.save()
			result.result_process(request.POST['testresult'], request.POST['testno'], request.POST['testcase'], testupload.id)
			return HttpResponseRedirect(reverse('poc:resultdetail', args=(request.POST['testno'],)))

	#####
	## for before upload result
	#####
	else:
		try:
			testcase = testCase.objects.all().order_by('test_name')
			latest_testtry = testTry.objects.all().aggregate(Max('test_no'))
			test_case = testTry.objects.select_related("testcase").get(test_no=latest_testtry['test_no__max'])
		except testTry.DoesNotExist:
			latest_testtry = 0
			test_case = ''
		context = {'testcase': testcase, 'latest_testtry':latest_testtry, 'test_case_name':test_case}
		return render(request, 'poc/upload_result.html', context)

def show_result_summary(request, testno):
	output_list = {'set1':[{'scenerio':0, 'ipv4':{'drop_time':0, 'dead':'no'}, 'ipv6':{'drop_time':0, 'dead':'no'}} for i in range(32)],\
					'set2':[{'scenerio':0, 'ipv4':{'drop_time':0, 'dead':'no'}, 'ipv6':{'drop_time':0, 'dead':'no'}} for i in range(26)],\
					'set3':[{'scenerio':0, 'ipv4':{'drop_time':0, 'dead':'no'}, 'ipv6':{'drop_time':0, 'dead':'no'}} for i in range(26)],\
					}
	# try:
	queried_flow = testResult.objects.select_related('testtry').filter(testtry__test_no=testno)
	testcase_name =queried_flow[0].testcase

	for row in queried_flow:
		scenerio = row.flow_name.split('_')[1]
		address_family = 'ipv6' if 'IPv6' in row.flow_name else 'ipv4'
		if row.flow_name.startswith('S1') and 'MCAST' not in row.flow_name:
			scenerio = int(scenerio)
			if output_list['set1'][scenerio-1][address_family]['drop_time'] < row.drop_time:
				output_list['set1'][scenerio-1][address_family]['drop_time'] = row.drop_time
			output_list['set1'][scenerio-1]['scenerio'] = scenerio
			if row.tx - row.rx != 0 :
				output_list['set1'][scenerio-1][address_family]['dead'] = 'yes' if (((row.tx - row.rx) - row.drop_count) /(row.tx - row.rx)) *100  > 30 else 'no'
			else:
				output_list['set1'][scenerio-1][address_family]['dead'] = 'no'
		elif row.flow_name.startswith('S2') and 'MCAST' not in row.flow_name:
			scenerio = int(scenerio)
			if output_list['set2'][scenerio-1][address_family]['drop_time'] < row.drop_time:
				output_list['set2'][scenerio-1][address_family]['drop_time'] = row.drop_time
			output_list['set2'][scenerio-1]['scenerio'] = scenerio
			if row.tx - row.rx != 0 :
				output_list['set2'][scenerio-1][address_family]['dead'] = 'yes' if (((row.tx - row.rx) - row.drop_count) /(row.tx - row.rx)) *100  > 30 else 'no'
			else:
				output_list['set2'][scenerio-1][address_family]['dead'] = 'no'
		elif row.flow_name.startswith('S3') and 'MCAST' not in row.flow_name:
			scenerio = int(scenerio)
			if output_list['set3'][scenerio-1][address_family]['drop_time'] < row.drop_time:
				output_list['set3'][scenerio-1][address_family]['drop_time'] = row.drop_time
			output_list['set3'][scenerio-1]['scenerio'] = scenerio
			if row.tx - row.rx != 0 :
				output_list['set3'][scenerio-1][address_family]['dead'] = 'yes' if (((row.tx - row.rx) - row.drop_count) /(row.tx - row.rx)) *100  > 30 else 'no'
			else:
				output_list['set3'][scenerio-1][address_family]['dead'] = 'no'

		context = {'summary': output_list, 'testcase_name':testcase_name, 'testno':testno}
	return render(request, 'poc/result_summary.html', context)

def show_result_detail(request,testno):
	try:
		queried_flow = testResult.objects.select_related('testtry').filter(testtry__test_no=testno)
		testcase_name =queried_flow[0].testcase
		results = []
		for row in queried_flow:
			result_row = {}
			result_row['flow_name'] = row.flow_name
			result_row['id'] = row.id
			result_row['rx'] = row.rx
			result_row['tx'] = row.tx
			result_row['drop_count'] = row.drop_count
			result_row['drop_time'] = row.drop_time
			if row.tx - row.rx != 0 :
				result_row['dead'] = 'yes' if (((row.tx - row.rx) - row.drop_count) /(row.tx - row.rx)) *100  > 30 else 'no'
			else:
				result_row['dead'] = 'no'
			result_row['percent_drop'] = row.percent_drop
			result_row['test_no'] = row.testtry.test_no
			result_row['stream_set'] = row.stream_set
			results.append(result_row)

		context = {'results': results, 'testcase_name':testcase_name, 'testno':testno}
		return render(request, 'poc/result_detail.html', context)
	except testResult.DoesNotExist:
		return render(request, 'poc/result_detail.html')

def show_result_all(request):
	queried_flow = testTry.objects.select_related('testcase')
	context = {'rows': queried_flow}
	return render(request, 'poc/results.html', context)

def edit_remark(request):
	if request.method == 'POST':
		test_no = request.POST['test_no']
		remark = request.POST['remark']
		# print (test_no, remark)
		doc = testTry.objects.filter(test_no=test_no).update(remark=remark)

		return HttpResponseRedirect(reverse('poc:results'))

def chart_view(request, flow_id):
	flow_name = get_object_or_404(testResult, id=flow_id).flow_name
	testcase_id = get_object_or_404(testResult, id=flow_id).testcase_id
	test_description = get_object_or_404(testCase, id=testcase_id).test_description

	#From Chartit.
	#Step 1: Create a DataPool with the data we want to retrieve.
	chartdata = DataPool(
		series=
		[
			{
			 'options': { 'source': testResult.objects.filter(flow_name=flow_name ,testcase_id=testcase_id).order_by('pub_date')[:40] },
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
			'title': {'text': 'Flow: '+flow_name+' :: '+test_description},
			'yAxis': {'title' : {'text': 'Drop Time (ms)' }},
		}
	)

	#Step 3: Send the chart object to the template.
	return render(request,'poc/chart.html', {'chart': cht})

def ajax_form(request):
	testno = request.GET['testno']
	respond = {}
	try:
		name = testTry.objects.select_related("testcase").get(test_no=testno).testcase.test_name
		desc = testTry.objects.select_related("testcase").get(test_no=testno).testcase.test_description
		respond['description'] = desc
	except testTry.DoesNotExist:
		respond['description'] = "Please select"

	return JsonResponse(respond)

def settings_page(request):
	return render(request, 'poc/settings.html')
