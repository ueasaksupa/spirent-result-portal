from django.urls import path

from . import views

app_name = 'poc'
urlpatterns = [
	path('', views.show_result_all, name='home'),
	# path('tupload', views.template_upload_handler, name='tupload'),
	path('resultUpload', views.result_upload_handler, name='resultUpload'),
	# path('showtemplate', views.show_template, name='showtemplate'),
	# path('stat', views.show_stat, name='stat'),
	path('edit/remark', views.edit_remark, name='editremark'),
	path('results', views.show_result_all, name='results'),
	path('result/<int:testno>', views.show_result_detail, name='resultdetail'),
	path('result/summary/<int:testno>', views.show_result_summary, name='summary'),
	path('chart/<int:flow_id>', views.chart_view, name='chart'),
	# path('server_side_endpoint', views.server_side_db_get, name='server-side-endpoint'),
	path('ajax/form', views.ajax_form, name='ajaxform'),
	# path('topology', views.topology_view, name='topology'),
]