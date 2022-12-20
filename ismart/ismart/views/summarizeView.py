import json,requests,os
from django.shortcuts import render
from ismart.views.summarizer import summarize 
from django.http import JsonResponse

# Create your views here.
    
    
def display_summary(request):
    # url = 'https://raw.githubusercontent.com/iSmart-Research-Scholar/Summarization/main/radha2016.pdf?token=GHSAT0AAAAAABXMOBI34OEHNV6I4YFK5646Y2K3CSA'
    urli=request.GET.get('url')
    r = requests.get(urli, stream=True)
    
    with open('datafiles/pdf/file.pdf', 'wb') as f:
        f.write(r.content) 
    
    summary=summarize('datafiles/pdf/file.pdf')
    os.remove('datafiles/pdf/file.pdf')
    return JsonResponse({"summary":summary},safe=False)