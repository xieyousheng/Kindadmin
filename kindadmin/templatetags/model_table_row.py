from django import template
import datetime
from pository import models
from django.utils.safestring import mark_safe
import datetime
import json

register = template.Library()


@register.simple_tag
def get_querysets_str(querysets,type='name'):
    '''
    将querysets数据列表转换为字符串
    :param querysets:
    :return:
    '''
    if type == 'name':
        result = [i.__str__() for i in querysets]
    elif type == 'id':
        result = [str(i.id) for i in querysets]
        return '_'.join(result)
    return ' | '.join(result)


@register.simple_tag
def get_table_verbose(admin_class):
    '''
    获取表的verbose_name （中文名）
    :param admin_class:
    :return:
    '''
    model_name = get_model_name(admin_class)
    verbose = admin_class.model._meta.verbose_name_plural
    return  verbose if verbose else  model_name

@register.simple_tag
def related_model_list(data_obj):
    '''
    列出跟该条数据相关联的其他数据
    :param data_obj:
    :param admin_class:
    :return:
    '''
    ele = '<ul>'
    ele += '<li>%s : <a href="/kindadmin/%s/%s/%s/change/">%s</a></li>' \
           % (data_obj._meta.verbose_name_plural,
              data_obj._meta.app_label,
              data_obj._meta.model_name,
              data_obj.id,
              data_obj)
    for i in data_obj._meta.related_objects:

        if i.get_internal_type() == 'ManyToManyField':
            ele += '<ul><li>%s</li></ul>' % i.name
        else:

            for j in getattr(data_obj,'%s_set' % i.name).all():
                ele += related_model_list(j)
    ele += '</ul>'
    return  ele

@register.simple_tag
def get_selected_m2m_data(filed_name,form_obj):
    '''
    获取以选取的字段
    :param filed_name:
    :param admin_class:
    :param form_obj:
    :return:
    '''
    try:
        return getattr(form_obj.instance ,filed_name).all()
    except Exception as e:
        print(e)
        return  ''

@register.simple_tag
def get_available_m2m_data(filed_name,admin_class,form_obj):
    '''
    返回m2m字段关联表的所有数据
    :param filed_name:
    :param admin_class:
    :return:
    '''
    data_obj = set(admin_class.model._meta.get_field(filed_name).related_model.objects.all())

    try:
        select_data = set(get_selected_m2m_data(filed_name,form_obj))
        data_obj = data_obj - select_data
    except Exception as e:
        print(e)

    return data_obj

@register.simple_tag
def get_field_value(filed,data_obj,admin_class):
    '''
    根据字段反射值
    filed 字段名
    data_obj 数据库记录
    admin_class
    :return:
    '''
    if admin_class.model._meta.get_field(filed).choices:
        #如果该字段为choice ，就返回choice的value值
        return getattr(data_obj,'get_%s_display'% filed)()
    else:
        return getattr(data_obj,filed)

@register.simple_tag
def get_verbose_name(filed,admin_class):
    '''
    根据字段获取verbose_name别名
    :param filed:
    :param admin_class:
    :return:
    '''
    rname = admin_class.model._meta.get_field(filed)._verbose_name
    return rname if rname else filed

@register.simple_tag
def search_placeholder(admin_class):
    '''
    返回搜索框里的placeholder显示内容
    :param admin_class:
    :return:
    '''
    search = '['
    for i in admin_class.search_fields:
        rname = get_verbose_name(i,admin_class)
        search += '%s|' % rname
    return search+']'



@register.simple_tag
def render_url_geturi(request,*args):
    '''
    返回url 以get请求的参数部分，args是排除哪些参数
    :param request:
    :param args:
    :return:
    '''
    inp = ''
    for k,v in request.GET.items():
        if k in args:continue
        if k:
            inp += '<input type="text" value="%s" name="%s" class="hidden">' %(v,k)
    return mark_safe(inp)

@register.simple_tag
def get_handel_id(request,handel_str):
    '''
    获取处理的id号，有则返回没有则返回空
    :param request:
    :param handel_str:
    :return:
    '''
    res = request.GET.get(handel_str)
    res = res if res else ''
    return res

@register.simple_tag
def convert(pageitem):
    '''
    把分页标签字符串转换为html
    :param pageitem:
    :return:
    '''
    return mark_safe(pageitem)

# use simple tag to show string
@register.simple_tag
def table_head(head_th,admin_class,index,request):
    url_str = ''
    span = ''
    for k,v in request.GET.items():
        if k in ['_o','p']:continue
        if k:
            url_str += '&%s=%s' % (k,v)
    o = index
    old_o =  request.GET.get('_o')
    if old_o and abs(int(old_o)) == o:
        o = -(int(old_o))
        if o > 0:
            span = '<span class="glyphicon glyphicon-triangle-bottom" aria-hidden="true"></span> '
        else:
            span = '<span class="glyphicon glyphicon-triangle-top" aria-hidden="true"></span>'
    rname = get_verbose_name(head_th,admin_class)
    th = '<th><a href="?_o=%s%s">%s</a>&nbsp&nbsp %s</th>' % (o,url_str ,rname,span)
    return mark_safe(th)


@register.simple_tag
def table_row(model_obj,admin_class):
    tr = '<tr>'
    tr +='<td><input  name="check_id" type="checkbox" value="%s"></td>' % model_obj.id
    if admin_class.list_display:
        for index,column in enumerate(admin_class.list_display):
            content = get_field_value(column,model_obj,admin_class)
            content = content if    content else '- -'
            if index == 0:
                td =  '<td scope="row"><a href="/kindadmin/%s/%s/%s/change/">%s</a></td>'
                tr += td % (admin_class.model._meta.app_label,admin_class.model._meta.model_name,model_obj.id,content)
            else:
                td = '<td scope="row">%s</td>'
                tr += td % content
    else:
        td = '<td scope="row"><a href="/kindadmin/%s/%s/%s/change/">%s</a></td>' % \
             (admin_class.model._meta.app_label,admin_class.model._meta.model_name,model_obj.id,model_obj)
        tr += td
    return mark_safe(tr)

@register.simple_tag
def filter_select(filter_name,admin_class):
    verbose_name = get_verbose_name(filter_name,admin_class)
    sel = '<span>%s：</span><select name="%s" class="form-control">' % (verbose_name,filter_name)
    try:
        for opt in admin_class.model._meta.get_field(filter_name).get_choices():
            select = ''
            if filter_name in admin_class.filter:
                if str(opt[0]) == admin_class.filter[filter_name]:
                    select = 'selected'
            option = '<option value="%s" %s>%s</option>' % (opt[0],select,opt[1])
            sel += option
    except AttributeError as e:
        if admin_class.model._meta.get_field(filter_name).get_internal_type() in ['DateField','DateTimeField']:
            sel = '<span>%s：</span><select name="%s__gte" class="form-control">' % (verbose_name,filter_name)
            op_list = [
                ('','------'),
                (datetime.date.today().strftime('%Y-%m-%d'),'今天'),
                ((datetime.date.today()+datetime.timedelta(days = -3)).strftime('%Y-%m-%d'),'3天内'),
                ((datetime.date.today()+datetime.timedelta(days = -7)).strftime('%Y-%m-%d'),'7天内'),
                (datetime.date.today().strftime('%Y-%m-1'),'1个月内'),
                ((datetime.date.today() + datetime.timedelta(days=-90)).strftime('%Y-%m-%d'), '3个月内'),
                ((datetime.date.today() + datetime.timedelta(days=-180)).strftime('%Y-%m-%d'), '半年内'),
                (datetime.date.today().strftime('%Y-1-1'), '1年内'),
            ]
            for opt in op_list:
                select = ''
                if '%s__gte'% filter_name in admin_class.filter:
                    if opt[0] == admin_class.filter['%s__gte'% filter_name]:
                        select = 'selected'
                option = '<option value="%s" %s>%s</option>' % (opt[0],select,opt[1])
                sel += option
    sel+='</select>'
    return mark_safe(sel)

@register.simple_tag
def get_app_name(admin_class):
    '''
    获取app_name
    :param admin_class:
    :return:
    '''
    return  admin_class.model._meta.app_label

@register.simple_tag
def get_model_name(admin_class):
    '''
    获取_model_name
    :param admin_class:
    :return:
    '''
    print(admin_class)
    return  admin_class.model._meta.model_name

@register.simple_tag
def get_admin_class(site,app_name,model_name):
    return  site[app_name][model_name]