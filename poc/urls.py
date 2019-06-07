from django.urls import path

from . import views

app_name = 'poc'
urlpatterns = [
    path('', views.show_all_results, name='home'),
    path('tupload', views.template_upload_handler, name='tupload'),
    path('rupload', views.result_upload_handler, name='rupload'),
    path('showtemplate', views.show_template, name='showtemplate'),
    # path('stat', views.show_stat, name='stat'),
    path('edit/remark', views.edit_remark, name='editremark'),
    path('result', views.show_all_results, name='result'),
    path('result/<int:test_set>', views.show_result, name='resultdetail'),
    path('result/summary/<int:test_set>', views.show_summary, name='summary'),
    path('chart/<int:flow_id>', views.chart_view, name='chart'),
    path('server_side_endpoint', views.server_side_db_get, name='server-side-endpoint'),
    path('auto/form', views.auto_form, name='auto-form'),
]