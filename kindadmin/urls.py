
from django.contrib import admin
from django.urls import path,include,re_path
from kindadmin import views
from kindadmin.views import account
from kindadmin.views import process_view

urlpatterns = [
    re_path('^$',process_view.KindAdmin.as_view()),
    path('login/',account.Login.as_view()),
    path('logout/',account.Logout.as_view()),
    path('create_code_img/', account.CreateImgCode.as_view()),
    re_path('^(?P<app_name>\w+)/$',process_view.AppObjList.as_view(),name='app_obj_list'),
    re_path('^(?P<app_name>\w+)/(?P<model_name>\w+)/$',process_view.tableobjlist,name='model_obj_list'),
    re_path('^(?P<app_name>\w+)/(?P<model_name>\w+)/add/$',process_view.AddTable.as_view(),name='add_model'),
    re_path('^(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<data_id>\d+)/change/$',process_view.EditTable.as_view(),name='edit_model'),
    re_path('^(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<data_id>\d+)/delete/$',process_view.DeleteTable.as_view(),name='delete_model'),

]
