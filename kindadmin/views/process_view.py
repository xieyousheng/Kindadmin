from django.shortcuts import render,HttpResponse,redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View
from  kindadmin.admin_site import site
from  kindadmin.pager import Pagination
from kindadmin import automatic_modelform
from django.db.models import Q
import json


@login_required
def deletetable(request,app_name,model_name,data_id):
        data_id = data_id.split('_')
        data_id = [int(i) for i in data_id]
        admin_class = site.site_dict[app_name][model_name]
        querysets = admin_class.model.objects.filter(id__in=data_id)
        if request.method == 'POST':
            querysets.delete()
            return redirect('/kindadmin/%s/%s/' % (app_name, model_name))
        return render(request,'kindbackend/table_obj_delete.html',locals())



@method_decorator(login_required,'dispatch')
class AppObjList(View):

    def get(self,request,app_name):
        model_obj_list = site.site_dict[app_name]
        result = {
            'app_name':app_name,
            'model_obj_list' : model_obj_list,
            'admin_class' : site.site_dict
        }
        return render(request,'kindbackend/app-obj-list.html',result)

def filter_handle(request,admin_class):
    filter_dict = {}
    for key,value in request.GET.items():
        if value:
            if key not in  ['p','_o','_q']:
                filter_dict[key] = value
    admin_class.filter = filter_dict
    model_data = admin_class.model.objects.filter(**filter_dict).only(*(admin_class.list_display if admin_class.list_display else []))

    return  model_data

def order_handle(request,model_data,admin_class):
    url_o = request.GET.get('_o')
    if url_o:
        if url_o.startswith('-'):
            model_data = model_data.order_by('-%s' % admin_class.list_display[abs(int(url_o))-1])
        else:
            model_data = model_data.order_by(admin_class.list_display[int(url_o) - 1])
    return model_data

def search_handle(request,model_data,admin_class):
    url_q = request.GET.get('_q')
    if url_q:
        q = Q()
        q.connector = 'OR'
        for i in admin_class.search_fields:
            q.children.append(('%s__contains'% i,url_q))
        model_data = model_data.filter(q)

    return model_data

@method_decorator(login_required,'dispatch')
class AddTable(View):
    def get(self,request,app_name,model_name):
        admin_class = site.site_dict[app_name][model_name]
        model_form = automatic_modelform.CreateModelForm(admin_class,False)
        from_obj = model_form()
        return render(request,'kindbackend/table_obj_add.html',locals())

    def post(self,request,app_name,model_name):
        admin_class = site.site_dict[app_name][model_name]
        model_form = automatic_modelform.CreateModelForm(admin_class,False)
        from_obj = model_form(data = request.POST)
        if from_obj.is_valid():
            from_obj.save()
            return  redirect('/kindadmin/%s/%s' % (app_name,model_name))
        else:
            return render(request,'kindbackend/table_obj_add.html',locals())

@method_decorator(login_required,'dispatch')
class EditTable(View):
    def get(self,request,app_name,model_name,data_id):
        admin_class = site.site_dict[app_name][model_name]
        model_form = automatic_modelform.CreateModelForm(admin_class)
        obj = admin_class.model.objects.get(id=data_id)
        from_obj = model_form(instance=obj)
        return render(request,'kindbackend/table_obj_change.html',locals())

    def post(self,request,app_name,model_name,data_id):
        admin_class = site.site_dict[app_name][model_name]
        model_form = automatic_modelform.CreateModelForm(admin_class)
        obj = admin_class.model.objects.get(id=data_id)
        print(request.POST)
        from_obj = model_form(instance=obj,data = request.POST)
        if from_obj.is_valid():
            from_obj.save()
            return  redirect('/kindadmin/%s/%s' % (app_name,model_name))
        else:
            return render(request,'kindbackend/table_obj_change.html',locals())

@login_required
def tableobjlist(request,app_name,model_name):
    admin_class = site.site_dict[app_name][model_name]
    model_data = filter_handle(request,admin_class).order_by('-id')
    model_data = order_handle(request,model_data,admin_class)
    model_data = search_handle(request,model_data,admin_class)
    page = Pagination(model_data,request.GET,pageItemLs=admin_class.list_per_page)
    model_data = page.get_item()
    pageitem = page.item_list()
    if request.method == 'POST':
        action_name = request.POST.get('action')
        id_list =  request.POST.get('check_id')

        querysets = admin_class.model.objects.filter(id__in=json.loads(id_list))
        if action_name:
            result = getattr(admin_class, action_name)(request, querysets)
            if result:
                return result
    result = {
        'app_name': app_name,
        'model_name': model_name,
        'model_data' : model_data,
        'admin_class':admin_class,
        'pageitem' : pageitem
    }
    return render(request,'kindbackend/table-obj-list.html',result)



@method_decorator(login_required,'dispatch')
class KindAdmin(View):
    def get(self,request,*args,**kwargs):
        return render(request, 'kindbackend/kindindex.html',{'enable_app':site.site_dict})

