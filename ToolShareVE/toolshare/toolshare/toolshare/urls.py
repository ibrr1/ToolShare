from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static


urlpatterns = [
    url(r'^change_password/$', 'tool_share_app.views.change_password.change_password', name='change_password'),

    url(r'^incoming_tool_requests/$', 'tool_share_app.views.incoming_tool_requests.incoming_tool_requests',
    name='incoming_tool_requests'),

    url(r'^delete_notifiation/(?P<notification_id>[0-9]+)/$', 'tool_share_app.views.notifications.delete_notification',
    name='notifications_delete'),

    url(r'^notifications/$', 'tool_share_app.views.notifications.notifications', name='notifications'),

    url(r'^accept_requested_tool/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.accept_requested_tool.accept_requested_tool',
    name='accept_requested_tool'),

    url(r'^cancel_requested_tool/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.cancel_requested_tool.cancel_requested_tool',
    name='cancel_requested_tool'),

    url(r'^cancel_request/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.delete_requested_tool.delete_requested_tool',
    name='delete_requested_tool'),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$','tool_share_app.views.login.user_login', name='login'),

    url(r'^registration/$', 'tool_share_app.views.registration.user_registration', name='registration'),

    url(r'^user_profile/$', 'tool_share_app.views.user_profile.user_profile', name='profile'),

    url(r'^user_profile/logout/$', 'tool_share_app.views.logout.logout', name='logout'),

    url(r'^shed_creation/$', 'tool_share_app.views.shed_registration.register_new_shed',
    name='new_shed'),

    url(r'^user_profile/update_account/$', 'tool_share_app.views.update_user_info.manage_account', name='modify_user_info'),

    url(r'^user_profile/manage_tools/(?P<tool_listing_type>[a-zA-Z_/]+)/$', 'tool_share_app.views.manage_tools.manage_tools',
    name='manage_tools_addition'),

    url(r'^user_profile/manage_tools/all_tools/delete/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.manage_tools.manage_tools_deletion_alt',
    name='manage_tools_deletion'),

    url(r'^user_profile/manage_tools/all_tools/(?P<tool_listing_type>[a-zA-Z_/]+)/delete/(?P<tool_id>[0-9]+)/$',
    'tool_share_app.views.manage_tools.manage_tools_deletion',
    name='manage_tools_deletion'),

    url(r'^user_profile/manage_tools/[a-zA-Z_ *0-9]+/update_tool/(?P<tool_id>[0-9]+)/$',  'tool_share_app.views.update_tool_info.update_tool',
    name='modify_tool_info'),

    url(r'^user_profile/manage_tools/[a-zA-Z_ *0-9]+/tool_profile/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.tool_profile.tool_profile',
    name='tool_profile'),

    url(r'^user_profile/manage_tools/all_tools/(?P<tool_listing_section>[a-zA-Z_]*)/request/(?P<tool_id>[0-9]+)/',
    'tool_share_app.views.tool_request.tool_request',
    name='tool_request'),

    url(r'^user_profile/requested_tools/', 'tool_share_app.views.requested_tools.requested_tools',
    name='requested_tools'),

    url(r'^user_profile/select_admin/$', 'tool_share_app.views.update_user_info.select_admin',
    name='select_admin'),

    url(r'^user_profile/select_admin/(?P<user_id>[0-9]+)/$', 'tool_share_app.views.update_user_info.make_user_admin',
    name='select_admin'),

    url(r'^user_profile/search/$', 'tool_share_app.views.search.search', 
    name='modify_user_info'),

    url(r'^user_profile/my_borrowed_tools/$', 'tool_share_app.views.my_borrowed_tools.borrowed_tools', 
    name='my_borrows_tools'),

    url(r'^tool_returned/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.my_borrowed_tools.returned_tool', 
    name='tool_returned'),

    url(r'^tools_in_possession/$', 'tool_share_app.views.tools_in_possession.tools_in_possession', 
    name='tools_in_possession'),

    url(r'^confirm_returned_tool/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.my_borrowed_tools.confirm_return', 
    name='confirm_returned_tool'),

    url(r'^reject_returned_tool/(?P<tool_id>[0-9]+)/$', 'tool_share_app.views.my_borrowed_tools.reject_return', 
    name='confirm_returned_tool'),

    url(r'^user_profile/user_information/(?P<user_id>[0-9]+)/$', 'tool_share_app.views.user_information.user_information',
    name='user_information'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)