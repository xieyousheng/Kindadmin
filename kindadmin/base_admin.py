from django.shortcuts import  render
import json

class BaseAdminSiet(object):
    def __init__(self):
        default_actions = ['delete_data', ]
        if hasattr(self,'actions'):
            self.actions.extend(default_actions)
        else:
            self.actions = default_actions



    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 5





    def delete_data(self,request,querysets):

        result = {
            'admin_class':self, #这里的self 就是admin_class ，因为在视图里是由admin_class反射的这个函数
            'querysets':querysets,
            'is_many':True
        }
        return  render(request,'kindbackend/table_obj_delete.html',result)
