from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from .models import Group
from .forms import GroupForm
from django.core import serializers
import json

def group_list(request):
    username = request.user.username if request.user.is_authenticated else 'niezalogowano'
    all_groups_list = Group.objects.order_by('name')
    context = {'models': all_groups_list, 'username': username}
    return render(request, 'groups/groups.html', context)
    
def add_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            new_group = form.save()
            data = serializers.serialize('json', [new_group])
            data = json.loads(data)
            data[0]['group_profile_name'] = str(new_group.group_profile)
            return HttpResponse(json.dumps(data))
    else:
        form = GroupForm()
    return HttpResponse(form) 
    
    
def edit_group(request):
    if request.method == "POST":
        try:
            record_id = request.POST['id']
            group = Group.objects.get(pk=record_id)
            form = GroupForm(request.POST, instance=group)
            if form.is_valid():
                new_group = form.save()
                data = serializers.serialize('json', [new_group])
                data = json.loads(data)
                data[0]['group_profile_name'] = str(new_group.group_profile)
                return HttpResponse(json.dumps(data))
        except ObjectDoesNotExist:
            raise Http404("Brak klasy o id %s w bazie." % record_id)
    elif request.method == "GET":
        try:
            record_id = request.GET['id']
            group = Group.objects.get(pk=record_id)
            form = GroupForm(instance=group)
        except ObjectDoesNotExist:
            raise Http404("Brak klasy o id %s w bazie." % record_id)
        return HttpResponse(form)

def delete_group(request):
    if request.method == "POST":
        record_id = request.POST.get("id")
        try:
            group = Group.objects.get(pk=record_id)
        except ObjectDoesNotExist:
            raise Http404("Brak klasy o id %s w bazie." % record_id)
        group.delete()
        return HttpResponse()