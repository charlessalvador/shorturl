from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from .models import Url,File,Export
import hashlib
from django.views.generic.base import View,TemplateView
from .forms import FileForm
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
import csv
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.core import serializers

# Create your views here.
def UrlCreate(long_url, fileformid,phone):
    if Url.objects.filter(
            long_url=long_url
    ).exists():  # If a shortened URL already exists, don't make a duplicate.

        return Url.objects.get(long_url=long_url), False

    try:
        hashed = hashlib.sha3_256(long_url.encode("utf-8")).hexdigest()

    except AttributeError:
        hashed = hashlib.sha256(long_url.encode("utf-8")).hexdigest()
    length = 5

    while Url.objects.filter(short_id=hashed[:length]).exists():
        length += 1

    url = Url(short_id=hashed[:length], long_url=long_url, fileid=File.objects.get(id=fileformid))
    url.save()
    phone=Export(phone=phone,short_id=hashed[:length],name=File.objects.get(id=fileformid).file)
    phone.save()

    pass

class RedirectView(View):
    def get(self, request, short):
        url = get_object_or_404(Url, short_id=short)

        if url.is_valida==False:
            if url.redirect_count<3:
                url.redirect_count += 1
                url.save()
                if url.redirect_count==3:
                    url.is_valida = True
                    url.save()
                    return redirect(url.long_url)

                return redirect(url.long_url)
        else:

            return redirect('/invalido')

    pass

class FileListView(ListView):
    model = File
    template_name = 'lista.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in File.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Archivos'
        context['create_url'] = reverse_lazy('shorturls:create')
        context['list_url'] = reverse_lazy('shorturls:list')
        context['entity'] = 'Files'

        return context

class FileCreateView(CreateView):
    model = File
    form_class = FileForm
    template_name = 'create.html'
    success_url = reverse_lazy('shorturls:list')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuevo archivo a convertir'
        context['entity'] = 'Files'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

class FileUpdateView(UpdateView):
    model = File
    form_class = FileForm
    template_name = 'procesar.html'
    success_url = reverse_lazy('shorturls:list')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'procesar':
                path=self.object.file
                fileformid=self.object.id
                with open('media/'+str(path), 'r+') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        UrlCreate(row['long_url'],fileformid,row['phone'])


            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Procesar un achivo'
        context['entity'] = 'Files'
        context['list_url'] = self.success_url
        context['action'] = 'procesar'
        return context

class FileDeleteView(DeleteView):
    model = File
    template_name = 'delete.html'
    success_url = reverse_lazy('shorturls:list')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            Url.objects.filter(fileid=self.object.id).delete()
            self.object.delete()

        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de Urls'
        context['entity'] = 'Files'
        context['list_url'] = self.success_url
        return context


class InvalidoView(TemplateView):
    template_name = 'invalido.html'


class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel'] = 'Panel de administrador'
        return context


class Exportview(View):

   def get(self, request,pk):
     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = 'attachment; filename="members.csv"'
     writer = csv.writer(response)
     writer.writerow(['phone', 'short_id','namefile'])
     filepath=File.objects.get(id=pk).file
     namepath=Export.objects.filter(name=filepath)
     for i in namepath:
         writer.writerow([i.phone,i.short_id,i.name])
     return response
