from datetime import datetime
from django.contrib import admin
from django.contrib.auth.models import User
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from main.models import Invitation, Confirmation, Section, Ticket, Show
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from django.core import serializers
import csv



def mark_as_sent(modeladmin, request, queryset):
    queryset.update(sent=True, sent_date=datetime.now())

def mark_as_intl_mail(modeladmin, request, queryset):
    queryset.update( i_delivery_mode='INTL')

def mark_as_typographical(modeladmin, request, queryset):
    queryset.update( is_typographical=True)

#def mark_as_celeb(modeladmin, request, queryset):
#    queryset.update(category='CELEB', sent=False, sent_date=None)

def t_mark_as_sent(modeladmin, request, queryset):
    queryset.update(sent=True, sent_date=datetime.now())

def c_mark_as_parking_allocated(modeladmin, request, queryset):
    queryset.update(parking_allocated=True)

c_mark_as_parking_allocated.short_description = _('Mark selected confirmations as PARKING allocated (YES!)')

def c_mark_as_parking_NOT_allocated(modeladmin, request, queryset):
    queryset.update(parking_allocated=False)

c_mark_as_parking_NOT_allocated.short_description = _('Mark selected confirmations as PARKING NOT allocated')

def c_mark_as_lounge(modeladmin, request, queryset):
    queryset.update(lounge=True)

c_mark_as_lounge.short_description = _('Mark selected confirmations with LOUNGE option=Yes')

def c_mark_as_lounge_off(modeladmin, request, queryset):
    queryset.update(lounge=False)

c_mark_as_lounge_off.short_description = _('Mark selected confirmations with LOUNGE option=NO')

def c_mark_as_category1(modeladmin, request, queryset):
    queryset.update(places_category=1)

c_mark_as_category1.short_description = _('Mark selected confirmations as PLACES CATEGORY=1')

def c_mark_as_category2(modeladmin, request, queryset):
    queryset.update(places_category=2)

c_mark_as_category2.short_description = _('Mark selected confirmations as PLACES CATEGORY=2')

def c_mark_as_category3(modeladmin, request, queryset):
    queryset.update(places_category=3)

c_mark_as_category3.short_description = _('Mark selected confirmations as PLACES CATEGORY=3')

def c_mark_as_category4(modeladmin, request, queryset):
    queryset.update(places_category=4)

c_mark_as_category4.short_description = _('Mark selected confirmations as PLACES CATEGORY=4')

def c_mark_as_category5(modeladmin, request, queryset):
    queryset.update(places_category=5)

c_mark_as_category5.short_description = _('Mark selected confirmations as PLACES CATEGORY=5')

def c_mark_as_card_sent(modeladmin, request, queryset):
    queryset.update(card_sent=True, card_sent_date=datetime.now())

c_mark_as_card_sent.short_description = _('Mark selected confirmations as CARD SENT')

def c_mark_places_allocated(modeladmin, request, queryset):
    queryset.update(places_allocated=True)

c_mark_places_allocated.short_description = _('Mark PLACES ALLOCATED for selected confirmations')


def export_to_file(modeladmin, request, queryset):
    response = HttpResponse(mimetype="text/csv")
    response['Content-Disposition'] = 'attachment; filename=invitations.csv'
   

    writer = csv.writer(response)
#    writer.writerow(['Year', 'Unruly Airline Passengers'])
#    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
#        writer.writerow([year, num])
    for row in queryset:
          writer.writerow(row[l_name])

#    serializers.serialize("json", queryset, stream=response)
    return response

mark_as_intl_mail.short_description = _('Mark selected invitations for International mailing')
mark_as_typographical.short_description = _('Mark selected invitations for Typographical personalisation')
export_to_file.short_description = _('Export selected invitations')
mark_as_sent.short_description = _('Mark selected invitations as sent')
# mark_as_celeb.short_description = _('Mark selected invitations as celebrities and not sent')
t_mark_as_sent.short_description = _('Mark selected confirmations as tickets sent')

class InvitationAdmin(ForeignKeyAutocompleteAdmin): #(admin.ModelAdmin):
    search_fields = ['l_name', 'f_name', 'code', 'company', ]
    list_display = ['code', 'show', 'post_date', 'category', 'l_name', 'f_name', 'company', 'user', 'i_delivery_mode', 'sent',  'inv_type', 'is_typographical', 'entrance', 'confirmed', 'sent_date', 'status', 'comment',]
    exclude = ('code',)
    list_filter = ('show', 'category', 'language', 'inv_type', 'confirmed', 'sent', 'i_delivery_mode', 'is_typographical', 'entrance', 'user',)
    readonly_fields = ('code',)
    fieldsets = [
        (_('To fill by manager'),{'description': _('Some of these fields will be visible to the guest. Please enter the field values carefully.'), 'fields': [ 'code', 'language', 'show', 'category', 'l_name','f_name','s_name','sex','company','position','contact_phone','mobile_phone','assistant_person','i_delivery_mode','t_delivery_mode','is_typographical','address','add_info','estimated_num','parking_place', 'inv_type','entrance',]}),
        (_('To fill by administrator'),{ 'classes': ('collapse',), 'fields': ['sent', 'sent_date', 'status', 'comment', 'confirmed','user',]}),
    ]
    actions = [mark_as_intl_mail,mark_as_typographical,mark_as_sent,] #'create_confirm'    
#    date_hierarchy = 'post_date'
    list_per_page = 950
#    list_per_page=50
    model = Invitation

    def create_confirm(self, request, queryset):
        for inv in queryset:
            Invitation.create_confirmation(inv.model)

    create_confirm.short_description = _('Create confirmations for selected invitations')

    def save_model(self, request, obj, form, change):
#        try:
#            obj.user:
#        except:

# TODO For regular user - revert changes from db, when change=True!!!
        if not obj.user or not change: #or not request.user.is_superuser:
            obj.user = request.user

        if not ( hasattr(obj, 'code')) or not obj.code:
            for i in range (1000):
                obj.code = User.objects.make_random_password(5, allowed_chars='0123456789')
                if Invitation.objects.filter(code=obj.code).count()==0:
                    break
						
        obj.save()

class TicketInLine(admin.TabularInline):
    model = Ticket

class ConfirmationAdmin(ForeignKeyAutocompleteAdmin):
    inlines = [TicketInLine,]
    search_fields = ['invitation__l_name', 'invitation__f_name', 'l_name', 'f_name', 'invitation__code', ]
    list_display = ['invitation', 'get_show','status', 'card_sent', 'sent', 'places_num', 'places_category', 'places_allocated', 'get_tix','lounge','get_parking_requested','parking_allocated', 'post_date','card_sent_date', 'sent_date','address', 'email', 'invitation']
    list_filter = ('status','invitation__show','invitation__category','invitation__language','places_category',  'places_allocated', 'lounge', 'invitation__parking_place','parking_allocated','card_sent','invitation__user',)
    list_editable = ['status','card_sent', 'sent', 'places_num', 'places_category', 'places_allocated', 'lounge','parking_allocated','address' ,]
    actions = [c_mark_as_parking_allocated,c_mark_as_parking_NOT_allocated,c_mark_as_lounge,c_mark_as_lounge_off,c_mark_as_card_sent, t_mark_as_sent,c_mark_as_category1,c_mark_as_category2,c_mark_as_category3,c_mark_as_category4,c_mark_as_category5, c_mark_places_allocated,]
    related_search_fields = {
        'invitation': ('code', 'f_name', 'l_name',),
    }
    list_per_page =950
#    list_per_page =50
    model = Confirmation

    def save_model(self, request, obj, form, change):
        obj.invitation.confirmed = True
        obj.invitation.save()
        obj.save()

class SectionAdmin(admin.ModelAdmin):
    pass

class TicketAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ['confirmation','__unicode__']
    related_search_fields = {
        'confirmation': ( 'invitation__code', 'f_name', 'l_name'), #'show',
    }

class ShowAdmin(admin.ModelAdmin):
    pass

admin.site.register(Invitation,InvitationAdmin)
admin.site.register(Confirmation,ConfirmationAdmin)
admin.site.register(Section,SectionAdmin)
admin.site.register(Ticket,TicketAdmin)
admin.site.register(Show,ShowAdmin)