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
from .models import testCase, testResult, testTry, testUpload, settings

def error_404_view(request, exception):
	return render(request,'poc/404.html')

def result_upload_handler(request):
	#####
	## for after upload result
	#####
	trigger_warning = False
	if request.method == 'POST' and request.POST['testresult']:
		testupload = testUpload(csv_result=request.POST['testresult'])
		testupload.save()
		###
		# this block is for existing test no.
		###
		try:
			tt = testTry.objects.get(test_no=request.POST['testno'])
			## check if all data can store correctly in data
			result_process_output = tt.result_process(request.POST['testresult'], request.POST['testno'], request.POST['testcase'], testupload.id)
			if result_process_output != 0:
			## if any error happend in this process not store any data and push alert
			## render same upload page with alert
				try:
					testcase = testCase.objects.all().order_by('test_name')
					latest_testtry = testTry.objects.all().aggregate(Max('test_no'))
					test_case = testTry.objects.select_related("testcase").get(test_no=latest_testtry['test_no__max'])
				except testTry.DoesNotExist:
					latest_testtry = {'test_no__max':1}
					test_case = ''
				trigger_warning = True
				error_msg = f"Found problem in result line {result_process_output[1]} . Please check if the CSV format is vaild or not." 
				context = {'testcase': testcase, 'latest_testtry':latest_testtry, 'test_case_name':test_case, 'trigger_warning': trigger_warning, "error_msg": error_msg}
				return render(request, 'poc/upload_result.html', context)
			# return render(request, 'poc/upload_result.html')
			return HttpResponseRedirect(reverse('poc:resultdetail', args=(request.POST['testno'],)))
		###
		# this block is for new test no.
		###
		except testTry.DoesNotExist:
			result = testTry(test_no=request.POST['testno'], testcase_id=request.POST['testcase'])
			result.save()
			## check if all data can store correctly in data
			result_process_output = result.result_process(request.POST['testresult'], request.POST['testno'], request.POST['testcase'], testupload.id)
			if result_process_output != 0:
			## if any error happend in this process not store any data and push alert
			## render same upload page with alert
				## delete current testTry because of it error.
				testTry.objects.filter(test_no=request.POST['testno']).delete()
				try:
					testcase = testCase.objects.all().order_by('test_name')
					latest_testtry = testTry.objects.all().aggregate(Max('test_no'))
					test_case = testTry.objects.select_related("testcase").get(test_no=latest_testtry['test_no__max'])
				except testTry.DoesNotExist:
					latest_testtry = {'test_no__max':1}
					test_case = ''
				trigger_warning = True
				error_msg = f"Found a problem in result line {result_process_output[1]} . Please check if the CSV format from spirent is vaild or not." 
				context = {'testcase': testcase, 'latest_testtry':latest_testtry, 'test_case_name':test_case, 'trigger_warning': trigger_warning, "error_msg": error_msg}
				return render(request, 'poc/upload_result.html', context)
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
			latest_testtry = {'test_no__max':1}
			test_case = ''
		context = {'testcase': testcase, 'latest_testtry':latest_testtry, 'test_case_name':test_case, 'trigger_warning': trigger_warning}
		return render(request, 'poc/upload_result.html', context)

def show_result_detail(request,testno):
	try:
		queried_flow = testResult.objects.select_related('testtry').filter(testtry__test_no=testno)
		testcase_name =queried_flow[0].testcase
		settings_object = settings.objects.first()
		delimiter = settings_object.delimiter
		Aend_index = settings_object.Aend_index
		Zend_index = settings_object.Zend_index
		tag_index = settings_object.tag_index
		
		trigger_warning = False
		result_dict = {}
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
			flow_name_sp_list = row.flow_name.split(delimiter)
			try:
				result_row['custom_col'] = {
					'source': flow_name_sp_list[Aend_index],
					'destination': flow_name_sp_list[Zend_index],
					'tag': flow_name_sp_list[tag_index]
				}
				result_row['is_custom_col_vaild'] = True
				if row.flow_name not in result_dict:
					update = {
						row.flow_name: {
							"tx": row.tx,
							"rx": row.rx,
							"id": row.id,
							"drop_count": row.drop_count,
							"drop_time": row.drop_time,
							"percent_drop": row.percent_drop,
							"test_no": row.testtry.test_no,
							"custom_col": {
								'source': flow_name_sp_list[Aend_index],
								'destination': flow_name_sp_list[Zend_index],
								'tag': flow_name_sp_list[tag_index]
							},
							"is_custom_col_vaild": True
						}
					}
					result_dict.update(update)
				elif result_dict[row.flow_name]["drop_time"] < row.drop_time:
					update = {
						row.flow_name: {
							"tx": row.tx,
							"rx": row.rx,
							"id": row.id,
							"drop_count": row.drop_count,
							"drop_time": row.drop_time,
							"percent_drop": row.percent_drop,
							"test_no": row.testtry.test_no,
							"custom_col": {
								'source': flow_name_sp_list[Aend_index],
								'destination': flow_name_sp_list[Zend_index],
								'tag': flow_name_sp_list[tag_index]
							},
							"is_custom_col_vaild": True
						}
					}
					result_dict.update(update)
			except IndexError:
				update = {
					row.flow_name: {
						"tx": row.tx,
						"rx": row.rx,
						"id": row.id,
						"drop_count": row.drop_count,
						"drop_time": row.drop_time,
						"percent_drop": row.percent_drop,
						"test_no": row.testtry.test_no,
						"is_custom_col_vaild": False
					}
				}
				result_dict.update(update)
				result_row['custom_col'] = {
					'source': '-',
					'destination': '-',
					'tag': '-'
				}
				result_row['is_custom_col_vaild'] = True
				trigger_warning = True
			results.append(result_row)

		if settings.objects.first().autogroup:
			results = []
			for flow_name, value in result_dict.items():
				if 'custom_col' in value:
					results.append(
						{
							"flow_name": flow_name,
							"tx": value['tx'],
							"rx": value['rx'],
							"id": value['id'],
							"drop_count": value['drop_count'],
							"drop_time": value['drop_time'],
							"percent_drop": value['percent_drop'],
							"test_no": value['test_no'],
							"custom_col": {
								'source': value['custom_col']['source'],
								'destination': value['custom_col']['destination'],
								'tag': value['custom_col']['tag']
							},
							"is_custom_col_vaild": True
						}
					)
				else:
					results.append(
						{
							"flow_name": flow_name,
							"tx": value['tx'],
							"rx": value['rx'],
							"id": value['id'],
							"drop_count": value['drop_count'],
							"drop_time": value['drop_time'],
							"percent_drop": value['percent_drop'],
							"test_no": value['test_no'],
							"custom_col": {
								'source': "-",
								'destination': "-",
								'tag': "-"
							},
							"is_custom_col_vaild": True
						}
					)
			context = {'results': results, 'testcase_name':testcase_name, 'testno':testno, 'trigger_warning':trigger_warning}
		else:
			context = {'results': results, 'testcase_name':testcase_name, 'testno':testno, 'trigger_warning':trigger_warning}
		return render(request, 'poc/result_detail.html', context)
	except testResult.DoesNotExist:
		return render(request, 'poc/result_detail.html')
	except IndexError:
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
	#####
	## for post method to submit setting changes
	#####
	if request.method == 'POST' and request.POST['delimiter']:
		delimiter = request.POST['delimiter']
		Aend_index = request.POST['Aend_index']
		Zend_index = request.POST['Zend_index']
		tag_index = request.POST['tag_index']
		
		setting = settings.objects.first()
		setting.delimiter = delimiter
		setting.Aend_index = Aend_index
		setting.Zend_index = Zend_index
		setting.tag_index = tag_index

		try:
			request.POST['checkbox']
			setting.autogroup = True
		except:
			setting.autogroup = False


		setting.save()
		return HttpResponseRedirect(reverse('poc:settings'))
	#####
	## for render setting page
	#####
	else:
		try:
			context = settings.objects.first() 
			return render(request, 'poc/settings.html', {'context': context})
		except settings.DoesNotExist:
			return render(request, 'poc/settings.html')
