from  . base_admin import BaseAdminSiet

class AdminSite(BaseAdminSiet):
    def __init__(self):
        self.site_dict = {}

    def register(self,model_name,class_name=None):
        if not class_name:
            class_name = BaseAdminSiet()
        else:
            class_name = class_name()
        class_name.model = model_name
        app_name = model_name._meta.app_label
        model_name = model_name._meta.model_name

        if app_name not in self.site_dict:
            self.site_dict[app_name] = {}
        self.site_dict[app_name][model_name] = class_name

site = AdminSite()