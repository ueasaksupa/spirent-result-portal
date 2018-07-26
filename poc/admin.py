from django.contrib import admin

from .models import FlowTemplate, Document, Flows, FlowSummary
# Register your models here.
admin.site.register(Flows)
admin.site.register(FlowTemplate)
admin.site.register(Document)
admin.site.register(FlowSummary)

