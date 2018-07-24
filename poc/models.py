from django.db import models
from django.utils import timezone
from django.conf import settings
from openpyxl import Workbook
from openpyxl import load_workbook
import os
import datetime

# Create your models here.

class Document(models.Model):
    path = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100,default='')
    def __str__(self):
        return self.description
    def __open_collector(self,start_collect_row,key_index,filename,sheetname):
        values_dict = {}

        wb = load_workbook(filename = filename)
        worksheet = wb[sheetname]
        column_header_index = {}
        column_header = []
        ### header
        header_count = 0
        for row in worksheet['A'+str(start_collect_row):'Z'+str(start_collect_row)]:
            for cell in row:
                if cell.value != None:
                    column_header.append(cell.value)
                    column_header_index[cell.value] = header_count
                    header_count += 1
                else:
                    break
        ###
        start_cell_id = ord('A')
        for row in range(start_collect_row+1,1000):
            for col in range(0,25):
                iter = chr(start_cell_id+col)+str(row)
                if worksheet[iter].value != None:
                    fix_A_cell = chr(ord(key_index))+str(row)
                    if 'A' in iter:
                        values_dict[worksheet[fix_A_cell].value.strip()] = [worksheet[iter].value]
                    else:
                        values_dict[worksheet[fix_A_cell].value.strip()].append(worksheet[iter].value)
                else:
                    break
        return values_dict, column_header, column_header_index

    def upload_template(self):
        MEDIA_DIR = settings.BASE_DIR+str(self.path)
        template_dict, template_header, theader_index = self.__open_collector(1,'A',MEDIA_DIR,'Result')
        for key,value in template_dict.items():
            try:
                flow = FlowTemplate.objects.get(flow_name=key)
                flow.fps = value[1]
                flow.id = str(self.id)
            except FlowTemplate.DoesNotExist:
                flow = FlowTemplate(flow_name=key.strip(), fps=value[1], document_id=str(self.id))
            finally:
                flow.save()

    def upload_result(self,testcase):
        MEDIA_DIR = settings.BASE_DIR+str(self.path)
        template_dict, template_header, theader_index = self.__open_collector(4,'C',MEDIA_DIR,'Advanced Sequencing')
        for key,value in template_dict.items():
            if 'L2L3' in key.strip().upper():
                service_type = 'L2L3'
            elif 'L3' in key.strip().upper():
                service_type = 'L3'
            elif 'L2' in key.strip().upper():
                service_type = 'L2'
            flow = self.flows_set.create(flow_name=key.strip(), 
                                                pub_date=timezone.now(),
                                                test_set=str(testcase),
                                                tx=value[theader_index['Tx Count (Frames)']],
                                                rx=value[theader_index['Rx Count (Frames)']],
                                                drop_count=value[theader_index['Tx-Rx (Frames)']],
                                                service_type=service_type) 

class FlowTemplate(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    flow_name = models.CharField(max_length=200)
    fps = models.IntegerField(default=1000)
    def __str__(self):
        return self.flow_name

class Flows(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    flow_name = models.CharField(default="",max_length=200)
    pub_date = models.DateTimeField('date published')
    test_set = models.CharField(default="",max_length=100)
    tx = models.IntegerField(default=0)
    rx = models.IntegerField(default=0)
    drop_count = models.IntegerField(default=0)
    drop_time = models.IntegerField(default=0)
    service_type = models.CharField(max_length=100)
    def __str__(self):
        return self.flow_name+' drop: '+str(self.drop_count)
