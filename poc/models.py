from django.db import models
from django.utils import timezone
from django.conf import settings
# from openpyxl import Workbook
# from openpyxl import load_workbook
import csv
import re
import datetime

# Create your models here.

class settings(models.Model):
	delimiter = models.CharField(default=",", max_length=30)
	Aend_index = models.IntegerField(default=0)	
	Zend_index = models.IntegerField(default=0)	
	tag_index = models.IntegerField(default=0)	
	autogroup = models.BooleanField(default=True)

class testCase(models.Model):
	test_name = models.CharField(default="", max_length=200)
	test_description = models.CharField(default="", max_length=200)
	def __str__(self):
		return str(self.test_name) + "  ::  " + str(self.test_description)

class testUpload(models.Model):
	pub_date = models.DateTimeField('date published', default=timezone.now)
	csv_result = models.TextField(default='')
	def __str__(self):
		try:
			coresponding_relation = testResult.objects.filter(testupload_id=self.id)[0]
			testcase_id = coresponding_relation.testcase_id
			testTry_id = coresponding_relation.testtry_id
			test_no = str(testTry.objects.get(id=testTry_id).test_no)
			test_description = str(testCase.objects.get(id=testcase_id).test_description)
		except:
			test_no = ""
			test_description = ""
		return "testUpload no. " + str(self.id) + "  ::  test no. "+ test_no + "  ::  " + test_description

class testTry(models.Model):
	testcase = models.ForeignKey(testCase, on_delete=models.CASCADE, default="")
	test_no = models.IntegerField(default=0)
	remark = models.CharField(default="", max_length=200)
	pub_date = models.DateTimeField('date published', default=timezone.now)
	def __str__(self):
		return str(self.test_no)+"  ::  "+self.remark

	def result_process(self, testresultCSV, testno, testcase_id, testupload_id):

		bulk_instance = []
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
					flow_name = row[thead.index('StreamBlock Name')].strip()
					drop_count = row[thead.index('Dropped Count (Frames)')].replace(',','')
					drop_time = row[thead.index('Dropped Frame Duration (us)')].replace(',','')
					tx = row[thead.index('Tx Count (Frames)')].replace(',','')
					rx = row[thead.index('Rx Sig Count (Frames)')].replace(',','')
					if int(tx) <= 0 :
						percent_drop = -1
					else:
						percent_drop = float(drop_count) / float(tx) * 100

				except IndexError:
					## return -1 mean error happened.
					return (-1, counter)
				counter += 1
				bulk_instance.append(
					testResult(
						flow_name=flow_name.strip(),
						tx=tx,
						rx=rx,
						drop_count=drop_count,
						drop_time=round(float(drop_time)/1000 ,2),
						percent_drop=round(percent_drop,5),
						testtry_id=self.id,
						testcase_id=testcase_id,
						testupload_id=testupload_id
					)
				)
		testResult.objects.bulk_create(bulk_instance)
		## return 0 mean everthing fine
		return 0

class testResult(models.Model):
	testcase = models.ForeignKey(testCase, on_delete=models.CASCADE, default="")
	testtry = models.ForeignKey(testTry, on_delete=models.CASCADE, default="")
	testupload = models.ForeignKey(testUpload, on_delete=models.CASCADE, default="")
	flow_name = models.CharField(default="", max_length=200)
	tx = models.BigIntegerField(default=0)
	rx = models.BigIntegerField(default=0)
	pub_date = models.DateTimeField('date published', default=timezone.now)
	drop_count = models.BigIntegerField(default=0)
	drop_time = models.FloatField(default=0.0)
	percent_drop = models.FloatField(default=0.0)

	def __str__(self):
		return str(self.testtry_id)+':'+self.flow_name+' drop: '+str(self.drop_count)
