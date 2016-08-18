# -*- coding: utf-8 -*- 
#import django django.VERSION
from django.db import models
from django import forms
from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator,MinValueValidator
#from django.utils import translation
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

SEX_CHOICES = (
   ('F', _('Female')),
   ('M', _('Male')),
)

I_DELIVERY_CHOICES = (
    ('SLF', _('Pass personally')),
    ('COUR', _('Via courier')),
    ('INTL',_('International mailing')),
    ('SNDT', _('Send just ticket')),
)

I_TYPE_CHOICES = (
    ('I', _('Invitation')),
    ('T', _('Tickets')),
)


T_DELIVERY_CHOICES = (
    ('SLF', _('Pass personally')),
    ('COUR', _('Via courier')),
    ('INTL',_('International mailing')),
)

TW_DELIVERY_CHOICES = (
    ('SLF', _('Take personally')),
    ('COUR', _('Via courier')),
)

CATEGORY_CHOICES = (
    ('NORM', _('Common')),
    ('VIP P', _('VIP Partner')),
    ('VIP G', _('VIP Goverment')),
    ('CELEB', _('Celebrity')),
    ('GOV', _('Goverment')),
    ('STAGE', _('Stage Staff')),
#    ('BART', _('Barter')),
    ('JORN', _('Jornalists')),
#    ('DISNEY', _('Disney')),
#    ('PRIZE',_('Prize-winner')),
#    ('TARAS', _('Tarasova')),
)

PARKING_CHOICES = (
    ('-', _('No matter')),
    ('Y', _('Yes')),
    ('N', _('No')),
)

STATUS_CHOICES = (
    ('R', _('Rejected')),
    ('C', _('Confirmed')),
    ('D', _('Another date')),
)

# I.Verba 02.09.14 Changed to Show class (look at Entity in admin-page)

#SHOW_CHOICES = (
#    ('WOZ',_('The Wizard of Oz')),
#    ('CHG',_('CHICAGO')),
#    ('TLM', _('The Little Mermaid')),
#    ('MM', _('Mamma mia!')),
#    ('TTM',_('The Three Musketeers')),
#    ('AMM', _('ACTION on Mamma mia!')),
#    ('POTO', _('Phantom of The Opera')),
#    ('BATB', _('Beauty and The Beast')),
#    
#)

ENTRANCE_CHOICES = (
    ('N', _('Normal')),
    ('V', _('VIP')),
)

REG_CHOICES  = (
    ('N', _('not opened yet')),
    ('O', _('opened')),
    ('S', _('temporarily suspended')),
    ('C', _('closed already')),	
)


class Show(models.Model):
    show = models.CharField(_('Event code'), primary_key=True , max_length=16, null=False, blank=False)
    name = models.CharField(_('Event name'),max_length=128, null=False, blank=False)
    eng_name = models.CharField(_('International name of Event'), max_length=128, null=True, blank=True)
    event_time = models.DateTimeField(_('Event date&time'), null=False, blank=False)
    doors_open = models.TimeField(_('Doors open at'), null=True, blank=True)	
    venue = models.CharField(_('Venue (where?)'),max_length=128, null=False, blank=False)
    eng_venue = models.CharField(_('International name of Venue (where?)'), max_length=128, null=True, blank=True)
    address = models.CharField(_('Event address'),max_length=256, null=False, blank=False)
    eng_address = models.CharField(_('International address of Event'),max_length=256, null=True, blank=True)	
    send_mail = models.BooleanField(_('Send email to guests as result of registration'),default=True,null=False, blank=False)
    reg_status = models.CharField(_('Registration status'),max_length=1, null=False, blank=False, choices=REG_CHOICES,default='N')
	
    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
        ordering = ('-event_time','name')
#        unique_together = ('show','language',)
 
    def __unicode__(self):
        return u'%s' % self.name


class Invitation(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    post_date = models.DateTimeField(_('Post date'),auto_now_add=True)
    code = models.CharField(_('Invitation code'),max_length=5, unique=True)
    language = models.CharField(_('Language'),max_length=2, choices=settings.LANGUAGES, default='ru')
    category = models.CharField(_('Guest category'),max_length=16, choices=CATEGORY_CHOICES)
    l_name = models.CharField(_('Last name'),max_length=128)
    f_name = models.CharField(_('First name'),max_length=128)
    s_name = models.CharField(_('Middle name'),max_length=128, null=True, blank=True)
    sex = models.CharField(_('Sex'), max_length=1, choices=SEX_CHOICES)
    company = models.CharField(_('Company'),max_length=256)
    position = models.CharField(_('Position'),max_length=256)
    contact_phone = models.CharField(_('Contact phone'),max_length=64)
    mobile_phone = models.CharField(_('Mobile phone'),max_length=64)
    assistant_person = models.CharField(_('Assistant person'),max_length=128, null=True, blank=True)
    i_delivery_mode = models.CharField(_('Invitation delivery mode'),max_length=16, choices=I_DELIVERY_CHOICES)
    t_delivery_mode = models.CharField(_('Ticket delivery mode'),max_length=16, choices=T_DELIVERY_CHOICES)
    address = models.TextField(_('Address'),null=True, blank=True)
    status = models.CharField(_('Status'),max_length=128, null=True, blank=True)
    add_info = models.TextField(_('Additional information'),null=True, blank=True)
    estimated_num = models.SmallIntegerField(_('Estimated number of guests'),default=2)
    parking_place = models.CharField(_('Need a parking place'),max_length=1, choices=PARKING_CHOICES)
    sent = models.BooleanField(_('Invitation sent'),default=False)
    sent_date = models.DateTimeField(_('Sent date'), null=True, blank=True)
    show = models.ForeignKey(Show, verbose_name=_('Event'), db_index=False, db_column='show', null=False, blank=False)
    confirmed = models.BooleanField(_('Responce received'),default=False)
    comment = models.TextField(_('Comments'),null=True, blank=True)
    is_typographical=models.BooleanField(_('Typographical personalisation'),default=False)
    inv_type = models.CharField(_('Invitation type'),max_length=1, choices=I_TYPE_CHOICES, default='I')
    entrance = models.CharField(_('Entrance'),max_length=1, choices=ENTRANCE_CHOICES, default='N')

	
    class Meta:
        verbose_name = _('invitation')
        verbose_name_plural = _('invitations')
        ordering = ('-post_date',)

    def __unicode__(self):
        return u'%s %s (%s)' % (self.l_name, self.f_name, self.code)
		
class Confirmation(models.Model):
    invitation = models.OneToOneField(Invitation, verbose_name=_('invitation'))
    post_date = models.DateTimeField(_('Post date'),auto_now_add=True)
    l_name = models.CharField(_('Last name'),max_length=128, null=True, blank=True)
    f_name = models.CharField(_('First name'),max_length=128, null=True, blank=True)
    s_name = models.CharField(_('Middle name'),max_length=128, null=True, blank=True)
    company = models.CharField(_('Company'),max_length=256, null=True, blank=True)
    position = models.CharField(_('Position'),max_length=256, null=True, blank=True)
    contact_phone = models.CharField(_('Contact phone'),max_length=64, null=True, blank=True)
    email = models.EmailField(_('Email'), max_length=128, null=True, blank=True)
    address = models.TextField(_('Address'),null=True, blank=True)
    assistant_person = models.CharField(_('Assistant person'),max_length=128, null=True, blank=True)
    places_num = models.SmallIntegerField(_('Number of seats'), null=True, blank=True)
    comment = models.TextField(_('Comments'), null=True, blank=True)
    status = models.CharField(_('Status'),max_length=1, choices=STATUS_CHOICES)
    sent = models.BooleanField(_('Tickets sent'),default=False)
    sent_date = models.DateTimeField(_('Sent date'), null=True, blank=True)
    parking_allocated = models.BooleanField(_('Parking allocated'),default=False, null=False)
    card_sent=models.BooleanField(_('Card sent'),default=False,null=False)
    card_sent_date = models.DateTimeField(_('Card sent date'), null=True, blank=True)
    lounge=models.BooleanField(_('Lounge'),default=False,null=False)
    places_category=models.SmallIntegerField(_('Places category'), null=True, blank=True, validators=[MinValueValidator(1),MaxValueValidator(5),])
    places_allocated=models.BooleanField(_('Places_allocated'),default=False,null=False)
    mail_sent_date = models.DateTimeField(_('Mail sent date&time'), null=True, blank=True)
	
    class Meta:
        verbose_name = _('confirmation')
        verbose_name_plural = _('confirmations')
        ordering = ('-post_date',)

    def get_tix(self):
        return self.ticket_set.all().count()
    get_tix.short_description = _('Tickets issued')

    def get_parking_requested(self):
        return self.invitation.parking_place
    get_parking_requested.short_description = _('Need a parking place')

    def get_show(self):
        return self.invitation.show
    get_show.short_description = _('Event')

    def create_confirmation(self):
        inv=self
        if inv.confirmed==False:
            con = Confirmation()
            con.invitation = inv
            inv.confirmed=True
            con.status='C'
            con.f_name = inv.f_name 
            con.l_name = inv.l_name 
            con.s_name = inv.s_name 
            con.contact_phone = inv.contact_phone
            con.assistant_person = inv.assistant_person
            con.address = inv.address
            con.places_num = inv.estimated_num
            con.comment = inv.add_info
            con.company = inv.company
            con.position = inv.position
#            try:
#                con.save()
#            except:
#               raise Http404

#            inv.save()

    def __unicode__(self):
        return u'%s %s (%s)' % (self.invitation.l_name, self.invitation.f_name, self.invitation.code)

class Section(models.Model):
    name = models.CharField(_('Section name'),max_length=128)

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')
        ordering = ('name',)

    def __unicode__(self):
        return u'%s' % self.name

class Ticket(models.Model):
    confirmation = models.ForeignKey(Confirmation, verbose_name=_('confirmation'))
    section = models.ForeignKey(Section, verbose_name=_('section'))
    row = models.CharField(_('Row'),max_length=4)
    seat = models.CharField(_('Seat'),max_length=4)

    class Meta:
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')
        ordering = ('row' , 'seat',)
        unique_together = ('section', 'row', 'seat',)

    def __unicode__(self):
        return u'%s:(%s,%s)' % (self.section, self.row, self.seat)

def validate_code(value):
    invitations = Invitation.objects.filter(code=value)
#    invitations = Invitation.objects.filter(code=value, show__in=['POTO','BATB'])
#    invitations = Invitation.objects.select_related('show').filter(code=value)

    if invitations.count() == 0:
        raise ValidationError(['You have entered incorrect code. Please try again.',u'Введен неправильный код. Попробуйте еще раз.',]) #ugettext('You have entered incorrect code, please try again'),])	
#        raise ValidationError('You have entered incorrect code, please try again / '+ugettext('You have entered incorrect code, please try again'))
    elif invitations[0].confirmed is True:
        raise ValidationError(['This invitation is already registered. Please enter another code.',u'Указанный код подтверждения уже зарегистрирован. Пожалуйста, введите другой код.',])
#        raise ValidationError('This invitation is already registered, please, enter another code / '+ugettext('This invitation is already registered, please, enter another code'))

class CodeCheckForm(forms.Form):
    code = forms.CharField(label=_('Code'),max_length=5,validators=[validate_code])

class AnotherDateForm(forms.Form):
    l_name = forms.CharField(label=_('Last name'),max_length=128)
    f_name = forms.CharField(label=_('First name'),max_length=128)
    s_name = forms.CharField(label=_('Middle name'),max_length=128, required=False)
    contact_phone = forms.CharField(label=_('Contact phone'),max_length=64)
    email = forms.EmailField(label=_('Email'))

    def is_valid(self):
        ret = forms.Form.is_valid(self)
        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret

class CelebForm(forms.Form):
    l_name = forms.CharField(label=_('Last name'),max_length=128)
    f_name = forms.CharField(label=_('First name'),max_length=128)
    s_name = forms.CharField(label=_('Middle name'),max_length=128, required=False)
    contact_phone = forms.CharField(label=_('Contact phone'),max_length=64)
    assistant_person = forms.CharField(label=_('Contact person'),max_length=128, required=False)
    email = forms.EmailField(label=_('Your e-mail address to which you would like to receive reservation confirmation'))
    tix_num = forms.IntegerField(label=_('Total number of tickets to be reserved under Your name'))
    add_info = forms.CharField(label=_('Here You may leave your comments or ask a question to the Opening night Manager'), widget=forms.Textarea, required=False)

    def is_valid(self):
        ret = forms.Form.is_valid(self)
        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret

#class BaseOthersForm(forms.Form):
class OthersForm(forms.Form):
    l_name = forms.CharField(label=_('Last name'),max_length=128,widget = forms.TextInput(attrs={'readonly':'readonly'}))
    f_name = forms.CharField(label=_('First name'),max_length=128,widget = forms.TextInput(attrs={'readonly':'readonly'}))
    s_name = forms.CharField(label=_('Middle name'),max_length=128, required=False,widget = forms.TextInput(attrs={'readonly':'readonly'}) )
    contact_phone = forms.CharField(label=_('Contact phone'),max_length=64, required=True)
    assistant_person = forms.CharField(label=_('Contact person if other than above'),max_length=128, required=False)
    email = forms.EmailField(label=_('The email address at which you would like to receive the copy of the confirmation'))
#    tix_num = forms.IntegerField(label=_('Total number of tickets to be reserved under Your name'),validators=[MinValueValidator(1),MaxValueValidator(5),])
#    is_temp_addr = forms.BooleanField(label=_('Should we use this address as temporary only for this case?'),required=False)

#    isInvTix = False
#    address = forms.CharField(label=_('Delivery address for courier service'), widget=forms.Textarea, required=False)
 
    def is_valid(self):
        ret = forms.Form.is_valid(self)

        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret


class TixNumForm(OthersForm):
#I_TYPE_CHOICES = (
#    ('I', _('Invitation')),
#    ('T', _('Tickets')),
    tix_num = forms.ChoiceField(choices=[[1,1],[2,2],[3,3],[4,4],[5,5]],label=_('Total number of tickets to be reserved under Your name'),required=True)

class VIPForm(TixNumForm):
    pass
#    tix_num = forms.ChoiceField(choices=[[1,1],[2,2],[3,3]],label=_('Total number of tickets to be reserved under Your name'),required=True)
	
class NormalForm(TixNumForm):
#    isInvTix = True
    address = forms.CharField(label=_('Delivery address for courier service'), widget=forms.Textarea, required=True)

#class OthersForm(BaseOthersForm):
#    isInvTix = False
#    address = forms.CharField(label=_('Delivery address for courier service'), widget=forms.Textarea, required=False)

class PrizerForm(forms.Form):
    l_name = forms.CharField(label=_('Last name'),max_length=128)
    f_name = forms.CharField(label=_('First name'),max_length=128)
    s_name = forms.CharField(label=_('Middle name'),max_length=128, required=False)
    contact_phone = forms.CharField(label=_('Contact phone'),max_length=64, required=True)
    email = forms.EmailField(label=_('The email address at which you would like to receive an invitation to the concrete spectacle date'), required=True)
 
    def is_valid(self):
        ret = forms.Form.is_valid(self)

        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret

class TarasForm(forms.Form):
    l_name = forms.CharField(label=_('Last name'),max_length=128)
    f_name = forms.CharField(label=_('First name'),max_length=128)
    s_name = forms.CharField(label=_('Middle name'),max_length=128, required=False)
    contact_phone = forms.CharField(label=_('Contact phone'),max_length=64)
    t_delivery_mode = forms.CharField(label=_('Ticket delivery mode'), widget=forms.Select(choices=TW_DELIVERY_CHOICES))
    email = forms.EmailField(label=_('Your e-mail address to which you would like to receive reservation confirmation'))
    tix_num = forms.IntegerField(label=_('Total number of tickets to be reserved under Your name'))
    add_info = forms.CharField(label=_('Here You may leave your comments or ask a question to the Opening night Manager'), widget=forms.Textarea, required=False)

    def is_valid(self):
        ret = forms.Form.is_valid(self)
        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret

class TarasAddrForm(forms.Form):
    address = forms.CharField(label=_('Delivery address for courier service'), widget=forms.Textarea)

    def is_valid(self):
        ret = forms.Form.is_valid(self)
        for f in self.errors:
            self.fields[f].widget.attrs.update({'class': 'fieldError'})
        return ret
