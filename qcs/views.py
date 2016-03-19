import json

#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render
from django.core.urlresolvers import reverse

from .forms import ManageQCForm
from .models import Log_quality_control_schedule_by_log, Quality_controls, Quality_control_info_by_log, \
    Quality_control_info_by_quality_control, Quality_control_level_info_by_log
from .qcs import QCData

def load_all_quality_controls_json(request):
    quality_controls_data = Quality_controls.get_all_qcs()
    return HttpResponse(json.dumps(quality_controls_data), content_type='application/json')

def load_log_qc_info_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    json_request = params.get('json_request', '')
    log_qc_info_data = QCData.get_log_qc_info(log_id, json_request)
    return HttpResponse(json.dumps(log_qc_info_data), content_type='application/json')

def load_log_qc_values_json(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_qc_level = params.get('qc_level', '')
    json_request = params.get('json_request', '')
    log_qc_values_data = Quality_control_info_by_log.get_log_qc_values(log_id, log_qc_level, json_request)
    return HttpResponse(json.dumps(log_qc_values_data), content_type='application/json')

def manage_quality_control(request):
    params = request.GET
    init_qc_level = params.get('qc_level', '')
    init_qc_name = params.get('qc_name', '')
    init_qc_form = dict
    template = 'qcs/manage_quality_control.html'

    if init_qc_level:    #: Edit existing quality control
        quality_control_data = Quality_control_info_by_quality_control.get_qc(init_qc_level)
        if quality_control_data:
            quality_control_map = quality_control_data[0]
            init_qc_name = quality_control_map.get('qc_name')
            init_qc_description = quality_control_map.get('qc_description')
            init_qc_form = {
            'qc_level' : init_qc_level,
            'qc_name' : init_qc_name,
            'qc_description' : init_qc_description,
        }
        else:
            print("Couldn't load qc info from database!")
    else:   #: Add new quality control
        init_qc_form = {}

    form = ManageQCForm(request.POST or None, initial=init_qc_form)

    if form.is_valid():
        qc_level = form.cleaned_data['qc_level']
        qc_name = form.cleaned_data['qc_name']
        qc_description = form.cleaned_data['qc_description']

        if init_qc_level:
            try:
                Quality_controls(bucket=0, qc_level=init_qc_level).delete()
                Quality_control_info_by_quality_control(qc_level=init_qc_level).delete()
            except:
                print("Delete query failed!")

        Quality_controls.create(
            bucket=0,
            qc_level=qc_level,
            qc_name=qc_name,
            qc_description=qc_description
        )
        Quality_control_info_by_quality_control.create(
            qc_level=qc_level,
            qc_name=qc_name,
            qc_description=qc_description
        )
        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'qc_level' : init_qc_level,
        'qc_name' : init_qc_name,
        'form' : form
    }

    return render(request, template, context)

def delete_quality_control(request):
    params = request.GET
    qc_level = params.get('qc_level', '')
    try:
        Quality_controls(bucket=0, qc_level=qc_level).delete()
        Quality_control_info_by_quality_control(qc_level=qc_level).delete()
    except:
        print("Delete query failed!")

    url = reverse('sites:index')

    return HttpResponseRedirect(url)

def manage_log_qc_info(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'qcs/manage_log_qc_info.html'
    return render(request, template, {})

def manage_log_qc_values(request):
    params = request.GET
    log_id = params.get('log_id', '')
    log_name = params.get('log_name', '')
    template = 'qcs/manage_log_qc_values.html'
    return render(request, template, {})