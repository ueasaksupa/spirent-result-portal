from django.contrib import admin

from .models import FlowTemplate, Document, Flows
# Register your models here.
admin.site.register(Flows)
admin.site.register(FlowTemplate)
admin.site.register(Document)

