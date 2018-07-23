from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# Create your views here.

from .models import Document

def home(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        
        # save file path to DB
        d = Document(path=uploaded_file_url)
        d.save()

        return render(request, 'poc/home.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'poc/home.html')