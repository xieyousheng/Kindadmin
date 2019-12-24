from django.shortcuts import render,HttpResponse,redirect
from django.utils.decorators import method_decorator
from  utils import check_code
from io import BytesIO
from Crypto.PublicKey import RSA
from Crypto import  Random
from Crypto.Cipher import  PKCS1_v1_5
import base64
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

from kindadmin.discovery import autoDiscoveryAdmin
autoDiscoveryAdmin()

def rsa(func):
    def inner(request,*args,**kwargs):
        random_generator = Random.new().read
        rsa = RSA.generate(1024, random_generator)
        rsa_private_key = rsa.exportKey()
        rsa_public_key = rsa.publickey().exportKey()
        # 1. 以session的方式存储私钥，PKCS1格式
        # request.session['privkey'] = rsa_private_key.decode()
        # 2. 存储到静态文件
        # print(rsa_private_key)
        request.session['primary_key'] =rsa_private_key.decode()
        request.session['public_key'] = rsa_public_key.decode()

        return func(request,*args,**kwargs)
    return inner


class Login(View):
    @method_decorator(rsa)
    def get(self,request,*args,**kwargs):
        return render(request, 'kindbackend/login.html')

    def post(self,request,*args,**kwargs):
        code = request.POST.get('code').lower()
        error = ''
        if code != request.session.get('check_code').lower():
            error = '验证码不正确!'
            return render(request,'login.html',{'error':error})
        passwd = request.POST.get('password')
        user = request.POST.get('username')
        privkeystr = request.session.get('primary_key').encode()
        # privkey 为私钥对象，由n，e等数字构成
        privkey = RSA.importKey(privkeystr)
        cipher = PKCS1_v1_5.new(privkey)
        # 现将base64编码格式的password解码，然后解密，并用decode转成str
        password = cipher.decrypt(base64.b64decode(passwd.encode()), 'error').decode()
        user = authenticate(username=user,password=password)
        if user:
            login(request,user)
            return redirect(request.GET.get('next','/kindadmin/'))

        # return redirect(request.GET.get('next','/crm/'))
        error = '用户名或密码错误!'
        return render(request, '/kindadmin/login.html', {'error': error})

class Logout(View):
    def get(self,request):
        logout(request)
        return redirect('/kindadmin/login/')

class CreateImgCode(View):

    def get(self,request):
        f = BytesIO()  # 直接在内存开辟一点空间存放临时生成的图片
        img, code = check_code.create_validate_code()  # 调用check_code生成照片和验证码
        request.session['check_code'] = code  # 将验证码存在服务器的session中，用于校验
        # img.save(f1, 'PNG')  # 生成的图片放置于开辟的内存中
        img.save(f, 'PNG')  # 生成的图片放置于开辟的内存中
        return HttpResponse(f.getvalue())  # 将内存的数据读取出来，并以HttpResponse返回f.getvalue()