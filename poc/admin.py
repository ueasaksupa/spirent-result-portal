from django.contrib import admin

from .models import testCase, testResult, testTry, testUpload, settings
# Register your models here.
admin.site.register(testCase)
admin.site.register(testTry)
admin.site.register(testResult)
admin.site.register(testUpload)
admin.site.register(settings)