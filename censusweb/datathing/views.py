from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
# Create your views here.
    
def tracts(request, state, county='', tract='', extension=''):
    return render_to_response('datathing.html',
        {
            'state': state,
            'county': county,
            'tract': tract,
            'extension': extension,
        },
        context_instance=RequestContext(request))

def homepage(request):
    return render_to_response('homepage.html', context_instance=RequestContext(request))