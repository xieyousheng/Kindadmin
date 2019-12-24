from django.forms import ModelForm

def CreateModelForm(admin_class,is_change=True):
    class Meta:
        #ModelForm 的 Meta原类
        model = admin_class.model
        fields = '__all__'
        if is_change:
            exclude = admin_class.readonly_fields
        admin_class.is_change = is_change


    def __new__(cls,*args,**kwargs):
        # 动态的给生成的form元素加上css {'class': 'form-control'}
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs.update({'class': 'form-control'})
        return ModelForm.__new__(cls)

    #使用type动态生成类，然后返回
    dynamic_form = type('DynamicModelForm',(ModelForm,),{'Meta':Meta,'__new__':__new__})

    return dynamic_form