from django.contrib import admin

from .models import testCase, testResult, testTry, testUpload
# Register your models here.
admin.site.register(testCase)
admin.site.register(testTry)
admin.site.register(testResult)
admin.site.register(testUpload)