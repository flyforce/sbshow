from main.models import *
from django.template import RequestContext
from django.http import Http404
from django.shortcuts import *
from django.utils import translation
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
import time
import datetime
from django.utils.translation import ugettext_lazy as _

def page_not_found2(request, template_name='404.html'):
    return django.views.defaults.page_not_found(request, template_name)

def is_superrequest(request):
    return request.user.is_authenticated() and request.user.is_superuser
	
def reset_session_data(request):
    for k in ('confirmation','invitation'):
        if k in request.session:
            del request.session[k]

def registration_closed(request):
    context = RequestContext(request)
    return render_to_response('registration_closed.html', context)

def coming_soon(request):
    context = RequestContext(request)
    return render_to_response('registration_coming_soon.html', context)

def check_code(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CodeCheckForm(request.POST)
        if form.is_valid():
            req_code = form.cleaned_data['code']
            invitation = Invitation.objects.select_related('show').filter(code=req_code)[0]

            if invitation.show.reg_status == 'O' or is_superrequest(request):
                return redirect('main.views.attendance',code=req_code)
            else:
                translation.activate(invitation.language)
                request.LANGUAGE_CODE = invitation.language
                context = RequestContext(request)
                context['inv'] = invitation
                reset_session_data(request)
                return render_to_response('registration_closed.html', context)
        else:
            time.sleep(10)
    else:
        if not is_superrequest(request) and Show.objects.filter(reg_status='O').count() == 0:
            return redirect('main.views.coming_soon')
			
        form = CodeCheckForm()

    context['form'] = form
    return render_to_response('check_code.html', context)

def get_inv_or_404(code):
    try:
#        inv = Invitation.objects.select_related('show').get(code=code, confirmed=False) #, show__reg_status='O'
        inv = Invitation.objects.select_related('show').get(code=code) #, show__reg_status='O'
    except Invitation.DoesNotExist:
        raise Http404('func get_inv_or_404: Invitation with code=%s does not exist' % code)
    return inv if inv.confirmed==False else None

def restart(request):
    reset_session_data(request)	
    return redirect('/')		

def attendance(request, code):
#    inv = get_object_or_404(Invitation, code=code, show__in=['POTO','BATB'], confirmed=False)
#    inv = get_object_or_404(Invitation, code=code, show__reg_status='O', confirmed=False)
    inv = get_inv_or_404(code)
    if not inv:
        return restart(request)
    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language
    context = RequestContext(request)
    context['inv'] = inv
#    request.session['invitation'] = inv	
    return render_to_response('attendance.html', context)

def status(request, code, status): 
#    inv = get_object_or_404(Invitation, code=code)
#    inv = request.session.get('invitation', False)
#    inv = get_object_or_404(Invitation, code=code, show__reg_status='O', confirmed=False)
    inv = get_inv_or_404(code)
    if not inv:
        return restart(request)
    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language
    context = RequestContext(request)
    confirmation = Confirmation()
    confirmation.invitation = inv
    if status == 'R':
        confirmation.status = 'R'
        inv.confirmed = True
        confirmation.save() ###
        inv.save()
#        try:
#            confirmation.save()
#        except:
#            raise Http404('func status: confirmation.save for status==R failed (inv.code=%s)' % code)

        context['inv'] = inv
#        reset_session_data(request)
        return render_to_response('status-rejected.html', context)
#    elif status == 'D':
#        confirmation.status = 'D';
#        inv.confirmed = True
#        request.session['confirmation'] = confirmation
#        request.session['invitation'] = inv
#        return redirect('main.views.new_date')
    elif status == 'C':
        confirmation.status = 'C'
        inv.confirmed = True
        request.session['confirmation'] = confirmation
        request.session['invitation'] = inv

#        if inv.category == 'PRIZE':
#            return redirect('main.views.prizers')
#        if inv.category == 'CELEB':
#            return redirect('main.views.celeb')
#        elif inv.category == 'TARAS':
#            return redirect('main.views.taras')
#        else:
        return redirect('main.views.others')
    else:
        raise Http404('func status: status not in (R,C), inv.code=%s' % code)


def others(request):
    inv = request.session.get('invitation', False)
#    if not inv:
#        raise Http404('func others: inv = request.session.get failed')
    con = request.session.get('confirmation', False)
#    if not con:
#        raise Http404('func others: con = request.session.get failed')
    if not inv or not con:
        return restart(request)

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
#        form = TixOthersForm(request.POST) if inv.inv_type=='T' else OthersForm(request.POST) 
#        form.isInvTix = (inv.inv_type=='T')
        if inv.show.show in ['SPA','BATB','ALD','ICE']:
            if inv.entrance=='V' or inv.language=='en' or inv.category=='CELEB':
                form = VIPForm(request.POST)
            else:
                form = NormalForm(request.POST)
        else:
            form = OthersForm(request.POST)

        if form.is_valid():
            con.f_name = form.cleaned_data['f_name']
            con.l_name = form.cleaned_data['l_name']
            con.s_name = form.cleaned_data['s_name']

            con.contact_phone = form.cleaned_data['contact_phone']
            con.assistant_person = form.cleaned_data['assistant_person']
            con.email = form.cleaned_data['email']

            if 'address' in form.fields: #if form.isInvTix:
                con.address = form.cleaned_data['address']
#                if not form.cleaned_data['is_temp_addr']:
#                inv.address=con.address

            con.places_num = int(form.cleaned_data['tix_num']) if 'tix_num' in form.fields else inv.estimated_num

            con.comment = inv.add_info
            con.company = inv.company
            con.position = inv.position

###
            inv.confirmed = True
            con.save()
            inv.save()
#            try:
#                con.save()
#            except:
#                raise Http404('func others: con.save failed, inv.code=%s' % inv.code)

            context['inv'] = inv
            context['con'] = con
            reset_session_data(request)

#           '''Send email'''
            if inv.show.send_mail:
                email_confirm(con,context,is_raise_except=False)
            context['lpage'] = True
            return render_to_response('status-others_done.html', context)

    else:
        data={
            'f_name': inv.f_name,
            'l_name': inv.l_name,
            's_name': inv.s_name,
            'contact_phone': inv.contact_phone,
            'assistant_person': inv.assistant_person,
#            'address': inv.address,
            'email' : con.email,
#            'tix_num': inv.estimated_num,
        }

		
        if inv.show.show in ['SPA','BATB','ALD','ICE']:
            data['tix_num']= inv.estimated_num
            if inv.entrance=='V' or inv.language=='en' or inv.category=='CELEB':
                form=VIPForm(initial=data)
            else:
                data['address']=inv.address			
                form = NormalForm(initial=data) 
        else:
            form = OthersForm(initial=data)


    context['form'] = form
    context['inv'] = inv
    return render_to_response('status-others.html', context)

#           Send single confirmation by email
def email_confirm(con,context,is_raise_except=True):
    text_content = get_template('status-others_done-mail.txt').render(context)
    html_content = get_template('status-others_done-mail.html').render(context)
    try:
        msg = EmailMultiAlternatives(_('Gala Opening Night: attendance confirmed'),text_content, 'Stage Entertainment <gala@stage-musical.ru>', [con.email,])
        msg.attach_alternative( html_content, "text/html")
        msg.send()
        con.mail_sent_date=datetime.datetime.now()
        con.save()
    except:
        if is_raise_except: #Re-raise or ignore any exception at mailing?
            raise



			
def send_mail(request, show):
    context = RequestContext(request)
    lst=Confirmation.objects.select_related('invitation').filter(invitation__show=show,mail_sent_date__isnull=True,email__isnull=False,status='C')

    for con in lst:
        inv=con.invitation
        translation.activate(inv.language)
        request.LANGUAGE_CODE = inv.language
        context['inv'] = inv
        context['con'] = con
        email_confirm(con,context,is_raise_except=True)

    s='<br/>'.join(['%36s %24s, %6s, %36s, %s' % (c.l_name,c.f_name,c.invitation.code,c.email,c.mail_sent_date) for c in lst])
		
    html = "<html><body><p>%s</p> Total %s record(s) were processed</body></html>" % (s, lst.count())
    return HttpResponse(html)
		
def new_date(request):
    inv = request.session.get('invitation', False)
    if not inv:
        raise Http404
    con = request.session.get('confirmation', False)
    if not con:
        raise Http404

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
        form = AnotherDateForm(request.POST)
        if form.is_valid():
            con.f_name = form.cleaned_data['f_name']
            con.l_name = form.cleaned_data['l_name']
            con.s_name = form.cleaned_data['s_name']
            con.contact_phone = form.cleaned_data['contact_phone']
            con.email = form.cleaned_data['email']
            inv.confirmed = True
            inv.save()
            try:
                con.save()
            except:
                raise Http404

            context['inv'] = inv
            context['con'] = con
            reset_session_data(request)

#            '''Send email'''
            plaintext = get_template('status-newdate_done-mail.txt')
            html      = get_template('status-newdate_done-mail.html')
            text_content = plaintext.render(context)
            html_content = html.render(context)
            msg = EmailMultiAlternatives(_('Sleeping Beauty: tickets for other day'), text_content, 'Stage Entertainment <gala@stage-entertainment.ru>', [con.email,])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render_to_response('status-newdate_done.html', context)
    else:
        form = AnotherDateForm(initial={
            'f_name': inv.f_name,
            'l_name': inv.l_name,
            's_name': inv.s_name,
            'contact_phone': inv.contact_phone,
        })

    context['form'] = form
    return render_to_response('status-newdate.html', context)

def celeb(request):
    inv = request.session.get('invitation', False)
    if not inv:
        raise Http404
    con = request.session.get('confirmation', False)
    if not con:
        raise Http404

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
        form = CelebForm(request.POST)
        if form.is_valid():
            con.f_name = form.cleaned_data['f_name']
            con.l_name = form.cleaned_data['l_name']
            con.s_name = form.cleaned_data['s_name']
            con.contact_phone = form.cleaned_data['contact_phone']
            con.assistant_person = form.cleaned_data['assistant_person']
            con.email = form.cleaned_data['email']
            con.places_num = form.cleaned_data['tix_num']
            con.comment = form.cleaned_data['add_info']
            inv.confirmed = True
            inv.save()
            try:
                con.save()
            except:
                raise Http404

            context['inv'] = inv
            context['con'] = con
            reset_session_data(request)

            '''Send email'''
            plaintext = get_template('status-celeb_done-mail.txt')
            html      = get_template('status-celeb_done-mail.html')
            text_content = plaintext.render(context)
            html_content = html.render(context)
            msg = EmailMultiAlternatives(_('Sleeping Beauty: attendance confirmed'), text_content, 'Stage Entertainment <gala@stage-entertainment.ru>', [con.email,])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render_to_response('status-celeb_done.html', context)

    else:
        form = CelebForm(initial={
            'f_name': inv.f_name,
            'l_name': inv.l_name,
            's_name': inv.s_name,
            'contact_phone': inv.contact_phone,
            'assistant_person': inv.assistant_person,
            'tix_num': inv.estimated_num,
        })

    context['form'] = form
    return render_to_response('status-celeb.html', context)

def taras(request):
    inv = request.session.get('invitation', False)
    if not inv:
        raise Http404
    con = request.session.get('confirmation', False)
    if not con:
        raise Http404

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
        form = TarasForm(request.POST)
        if form.is_valid():
            con.f_name = form.cleaned_data['f_name']
            con.l_name = form.cleaned_data['l_name']
            con.s_name = form.cleaned_data['s_name']
            con.contact_phone = form.cleaned_data['contact_phone']
            con.t_delivery_mode = form.cleaned_data['t_delivery_mode']
            con.email = form.cleaned_data['email']
            con.places_num = form.cleaned_data['tix_num']
            con.comment = form.cleaned_data['add_info']
            if con.t_delivery_mode == 'SLF':
                inv.confirmed = True
                inv.save()
                try:
                    con.save()
                except:
                    raise Http404

                context['inv'] = inv
                context['con'] = con
                reset_session_data(request)

                '''Send email'''
                plaintext = get_template('status-taras-slf_done-mail.txt')
                html      = get_template('status-taras-slf_done-mail.html')
                text_content = plaintext.render(context)
                html_content = html.render(context)
                msg = EmailMultiAlternatives(_('Sleeping Beauty: attendance confirmed'), text_content, 'Stage Entertainment <gala@stage-entertainment.ru>', [con.email,])
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                return render_to_response('status-taras-slf_done.html', context)
            else:
                request.session['invitation'] = inv
                request.session['confirmation'] = con
                return redirect('main.views.taras_addr')

    else:
        form = TarasForm(initial={
            'f_name': inv.f_name,
            'l_name': inv.l_name,
            's_name': inv.s_name,
            'contact_phone': inv.contact_phone,
            't_delivery_mode': inv.t_delivery_mode,
            'tix_num': inv.estimated_num,
        })

    context['form'] = form
    return render_to_response('status-taras.html', context)

def taras_addr(request):
    inv = request.session.get('invitation', False)
    if not inv:
        raise Http404
    con = request.session.get('confirmation', False)
    if not con:
        raise Http404

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
        form = TarasAddrForm(request.POST)
        if form.is_valid():
            con.address = form.cleaned_data['address']
            inv.confirmed = True
            inv.save()
            try:
                con.save()
            except:
                raise Http404

            context['inv'] = inv
            context['con'] = con
            reset_session_data(request)

            '''Send email'''
            plaintext = get_template('status-taras-addr_done-mail.txt')
            html      = get_template('status-taras-addr_done-mail.html')
            text_content = plaintext.render(context)
            html_content = html.render(context)
            msg = EmailMultiAlternatives(_('Sleeping Beauty: attendance confirmed'), text_content, 'Stage Entertainment <gala@stage-entertainment.ru>', [con.email,])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render_to_response('status-taras-addr_done.html', context)

    else:
        form = TarasAddrForm(initial={
            'address': inv.address,
        })

    context['form'] = form
    return render_to_response('status-taras-addr.html', context)

def prizers(request):
    inv = request.session.get('invitation', False)
    if not inv:
        raise Http404
    con = request.session.get('confirmation', False)
    if not con:
        raise Http404

    translation.activate(inv.language)
    request.LANGUAGE_CODE = inv.language

    context = RequestContext(request)

    if request.method == 'POST':
        form = PrizerForm(request.POST)
        if form.is_valid():
            con.f_name = form.cleaned_data['f_name']
            con.l_name = form.cleaned_data['l_name']
            con.s_name = form.cleaned_data['s_name']

            con.contact_phone = form.cleaned_data['contact_phone']
            con.email = form.cleaned_data['email']
            con.comment = inv.add_info

            con.places_num = inv.estimated_num
            con.company = inv.company
#            con.position = inv.position

###
            inv.confirmed = True
            inv.save()
            try:
                con.save()
            except:
                raise Http404

            context['inv'] = inv
            context['con'] = con
            reset_session_data(request)

#           '''Send email'''
            plaintext = get_template('status-prizers_done-mail.txt')
            html      = get_template('status-prizers_done-mail.html')
            text_content = plaintext.render(context)
            html_content = html.render(context)
            msg = EmailMultiAlternatives(_('Mamma Mia!: attendance confirmed'), text_content, 'Stage Entertainment <gala@stage-entertainment.ru>', [con.email,])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return render_to_response('status-prizers_done.html', context)

    else:
        form = PrizerForm(initial={
            'f_name': con.f_name,
            'l_name': con.l_name,
            's_name': con.s_name,
            'contact_phone': con.contact_phone,
            'email' : con.email,
        })

    context['form'] = form
    return render_to_response('status-prizers.html', context)
