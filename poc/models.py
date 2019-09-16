from django.db import models
from django.utils import timezone
from django.conf import settings
# from openpyxl import Workbook
# from openpyxl import load_workbook
import csv
import re
import datetime

# Create your models here.

class mcastFPS(models.Model):
	flow_name = models.CharField(default="", max_length=200)
	fps = models.IntegerField(default=0)
	def __str__(self):
		return self.flow_name+"  ::  "+str(self.fps)

class testCase(models.Model):
	test_name = models.CharField(default="", max_length=200)
	test_description = models.CharField(default="", max_length=200)
	def __str__(self):
		return self.test_name+"  ::  "+self.test_description

class testUpload(models.Model):
	pub_date = models.DateTimeField('date published', default=timezone.now)
	csv_result = models.TextField(default='')

class testTry(models.Model):
	testcase = models.ForeignKey(testCase, on_delete=models.CASCADE, default="")
	test_no = models.IntegerField(default=0)
	remark = models.CharField(default="", max_length=200)
	pub_date = models.DateTimeField('date published', default=timezone.now)
	def __str__(self):
		return str(self.test_no)+"  ::  "+self.remark

	def result_process(self, testresultCSV, testno, testcase, testupload_id):
		bulk_instance = []
		time = timezone.now()
		
		reader = csv.reader(testresultCSV.split('\n'), delimiter=',')
		thead = []
		counter = 0
		for row in reader:
			if counter == 0:
				thead = row[0:]
				counter += 1
			else:
				if len(row) < 1 :
					continue
				try:
					############
					### for mcast
					if "MCAST" in row[thead.index('Stream Block')] :
						flow_name = row[thead.index('Stream Block')].strip()
						print (flow_name)
						fps = mcastFPS.objects.get(flow_name=flow_name).fps
						print (fps)
						drop_count = row[thead.index('Dropped Count (Frames)')].replace(',','')
						drop_time = (float(drop_count) / fps ) * 1000
						tx = row[thead.index('Tx Count (Frames)')].replace(',','')
						rx = row[thead.index('Rx Count (Frames)')].replace(',','')
						if int(tx) <= 0 :
							percent_drop = -1
						else:
							percent_drop = float(drop_count) / float(tx) * 100
						stream_set = 'multicast'
						bulk_instance.append(
							testResult( flow_name=flow_name.strip(),
										tx=tx,
										rx=rx,
										drop_count=drop_count,
										drop_time=round(drop_time,2),
										stream_set=str(stream_set),
										percent_drop=round(percent_drop,5),
										testtry_id=self.id,
										testcase_id=testcase,
										testupload_id=testupload_id
										)
						)
				############
				### for other stream will hit this block if error from stream block name
				except ValueError:
					flow_name = row[thead.index('StreamBlock Name')]
					drop_count = row[thead.index('Dropped Count (Frames)')].replace(',','')
					drop_time = row[thead.index('Dropped Frame Duration (us)')].replace(',','')
					tx = row[thead.index('Tx Count (Frames)')].replace(',','')
					rx = row[thead.index('Rx Sig Count (Frames)')].replace(',','')
					if int(tx) <= 0 :
						percent_drop = -1
					else:
						percent_drop = float(drop_count) / float(tx) * 100
					if "MCAST" in flow_name:
						stream_set = 'multicast'
					elif flow_name.startswith('S1'):
						stream_set = '1'
					elif flow_name.startswith('S2'):
						stream_set = '2'
					elif flow_name.startswith('S3'):
						stream_set = '3'
					else:
						stream_set = 'other'
					bulk_instance.append(
						testResult( flow_name=flow_name.strip(),
									tx=tx,
									rx=rx,
									drop_count=drop_count,
									drop_time=round(float(drop_time)/1000,2),
									stream_set=str(stream_set),
									percent_drop=round(percent_drop,5),
									testtry_id=self.id,
									testcase_id=testcase,
									testupload_id=testupload_id
									)
					)
		testResult.objects.bulk_create(bulk_instance)

class testResult(models.Model):
	testcase = models.ForeignKey(testCase, on_delete=models.CASCADE, default="")
	testtry = models.ForeignKey(testTry, on_delete=models.CASCADE, default="")
	testupload = models.ForeignKey(testUpload, on_delete=models.CASCADE, default="")
	flow_name = models.CharField(default="", max_length=200)
	stream_set = models.CharField(default="", max_length=50)
	tx = models.BigIntegerField(default=0)
	rx = models.BigIntegerField(default=0)
	pub_date = models.DateTimeField('date published', default=timezone.now)
	drop_count = models.BigIntegerField(default=0)
	drop_time = models.FloatField(default=0.0)
	percent_drop = models.FloatField(default=0.0)
	# service_type = models.CharField(max_length=200)

	def __str__(self):
		return str(self.testtry_id)+':'+self.flow_name+' drop: '+str(self.drop_count)
