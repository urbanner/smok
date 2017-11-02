# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import Class_profile, HoursAmount
from .forms import ClassProfileForm, HoursAmountForm
from django.core import serializers
from django.forms import inlineformset_factory
from subjects.models import Subject
import re
import json

def profiles(request):
    username = request.user.username if request.user.is_authenticated else 'niezalogowano'
    #class_profile = Class_profile.objects.order_by('name')
    all_profiles_list = Class_profile.objects.select_related().order_by('name')
    print(all_profiles_list)
    context = {'models': all_profiles_list, 'username': username}
    return render(request, 'class-profiles.html', context)
"""
def custom_form_field_callback(field, **kwargs):
    #subjects_query = Subject.objects.filter(filter_field=filter_value)
    if field.name == "subject":
        #return Subject(queryset= subjects_query)
        pass
    else:
         return field.formfield(**kwargs)
"""
def profile(request, profile_id):
    username = request.user.username if request.user.is_authenticated else 'niezalogowano'
    profile = Class_profile.objects.get(pk=profile_id)
    ha_models_in_profile = HoursAmount.objects.filter(profile=profile).order_by('subject')
    print(ha_models_in_profile)
    context = {'model': profile, 'username': username, 'ha_models_in_profile': ha_models_in_profile}
    return render(request, 'class-profile.html', context)

def add_subject_to_profile(request):
    if request.method == "GET":
        profile_id = request.GET['profile-id']
        profile = Class_profile.objects.get(pk=profile_id)
        ha_models_in_profile = HoursAmount.objects.filter(profile=profile)

        wanted_items = set()
        for s in Subject.objects.all():
            if s.name not in (ha.subject.name for ha in ha_models_in_profile):
                wanted_items.add(s.pk)
        data = serializers.serialize('json', Subject.objects.filter(pk__in=wanted_items))
        return HttpResponse(data)

    if request.method == "POST":
        profile_id = int(dict(request.POST)['profile-id'][0])
        existing_profile = Class_profile.objects.get(pk=profile_id)
        subjects = dict(request.POST)['subject-id']
        response_data = []

        for s in subjects:
            subject = Subject.objects.get(pk=s)
            new_ha = HoursAmount(profile=existing_profile, subject=subject)
            new_ha.save()
            response_data.append(subject.id)
        data = serializers.serialize('json', Subject.objects.filter(pk__in=response_data))
        print(data)
        return HttpResponse(data)

    return HttpResponse('')

def save_new_hoursno_on_profile(request):
    if request.method == "POST":
        try:
            profile_id = request.POST['profile-id']

            for key in request.POST.keys():
                if 'hoursamount' in key:
                    subject_id = re.search('hoursamount-(.+?)-subject', key).group(1)
                    try:
                        hoursamount_record = HoursAmount.objects.get(subject=subject_id, profile = profile_id)
                        new_number_of_hours = int(request.POST[key])
                        if new_number_of_hours != hoursamount_record.hoursno:
                            hoursamount_record.hoursno = new_number_of_hours
                            hoursamount_record.save()
                    except ObjectDoesNotExist:
                        raise Http404("Brak rekordów z requesta w bazie.")
            return HttpResponse('')
        except ObjectDoesNotExist:
            raise Http404("Brak profilu o id %s w bazie." % 's')
    else:
        return reverse_lazy('classProfiles:list')

def add_profile(request):
    if request.method == "POST":
        form = ClassProfileForm(request.POST)
        if form.is_valid():
            new_profile = form.save()
            data = serializers.serialize('json', [new_profile])
            return HttpResponse(data)
    else:
        form = ClassProfileForm()
    return HttpResponse(form)

def edit_profile(request):
    if request.method == "POST":
        try:
            record_id = request.POST['id']
            profile = Class_profile.objects.get(pk=record_id)
            form = ClassProfileForm(request.POST, instance=profile)
            if form.is_valid():
                new_profile = form.save()
                data = serializers.serialize('json', [new_profile])
                return HttpResponse(data)
        except ObjectDoesNotExist:
            raise Http404("Brak profilu o id %s w bazie." % record_id)
    elif request.method == "GET":
        try:
            record_id = request.GET['id']
            profile = Class_profile.objects.get(pk=record_id)
            form = ClassProfileForm(instance=profile)
        except ObjectDoesNotExist:
            raise Http404("Brak profilu o id %s w bazie." % record_id)
        return HttpResponse(form)

def delete_profile(request):
    if request.method == "POST":
        record_id = request.POST.get("id")
        try:
            profile = Class_profile.objects.get(pk=record_id)
        except ObjectDoesNotExist:
            raise Http404("Brak przedmiotu o id %s w bazie." % record_id)
        profile.delete()
        return HttpResponse()
