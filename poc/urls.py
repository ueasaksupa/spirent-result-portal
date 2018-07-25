from django.urls import path

from . import views

app_name = 'poc'
urlpatterns = [
    path('', views.show_result, name='home'),
    path('tupload', views.template_upload_handler, name='tupload'),
    path('rupload', views.result_upload_handler, name='rupload'),
    path('showtemplate', views.show_template, name='showtemplate'),
    path('stat', views.show_stat, name='stat'),
    path('result', views.show_result, name='result'),
    path('result/summary/<int:test_set>', views.show_summary, name='summary'),
    path('chart/<int:flow_id>', views.chart_view, name='chart')
]