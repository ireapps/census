from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
# Create your views here.

def theapi(request, extension):
    return render_to_response('datathing.html', {'extension': extension}, context_instance=RequestContext(request))