from main.models import *
from django.template import RequestContext
from django.http import Http404
from django.shortcuts import *
from django.utils import translation
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
import time
import datetime
from django.utils.translation import ugettext_lazy as _

class Con:
    email='ivan.verba@gmail.com'
	
def get_inv_or_404(code):
    try:
        inv = Invitation.objects.select_related('show').get(code=code) #, show__reg_status='O', confirmed=False)
    except Invitation.DoesNotExist:
        raise Http404
    return inv

def test(request):
#    now = datetime.datetime.now()
#    html = "<html><body>It is now %s.</body></html>" % now
#    return HttpResponse(html)
    inv = get_inv_or_404('09010')
    con = Con()
    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language
    context = RequestContext(request)
    context['inv'] = inv
    context['con'] = con
#    return render_to_response('status-others_done.html',context)  
    return render_to_response('test.html', context)
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
	
