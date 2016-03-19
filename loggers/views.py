import json
import uuid
#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render
from django.core.urlresolvers import reverse

from .forms import ManageLoggerTimeFormatForm
from .models import Logger_time_formats, Logger_time_format_by_logger_time_format, Logs_by_logger_time_format
from logs.models import Log_time_info_by_log

def load_all_logger_time_formats_json(request):
    params = request.GET
    json_request = params.get('json_request', '')
    logger_time_formats_data = Logger_time_formats.get_all_logger_time_formats(json_request)
    return HttpResponse(json.dumps(logger_time_formats_data), content_type='application/json')

def load_logger_time_format_json(request):
    params = request.GET
    logger_time_format_id = params.get('logger_time_format_id', '')
    logger_time_format_data = Logger_time_format_by_logger_time_format.get_logger_time_format(logger_time_format_id)
    return HttpResponse(json.dumps(logger_time_format_data), content_type='application/json')

def manage_logger_time_format(request):
    params = request.GET
    logger_time_format_id = params.get('logger_time_format_id', '')
    logger_time_format_name = params.get('logger_time_format_name', '')
    init_logger_time_format_form = dict
    init_logger_time_ids = []
    init_logger_time_id_types = {}
    template = 'loggers/manage_logger_time_format.html'

    if logger_time_format_id:    #: Edit existing logger time format
        logger_time_format_data = Logger_time_format_by_logger_time_format.get_logger_time_format(logger_time_format_id)
        if logger_time_format_data:
            logger_time_format_map = logger_time_format_data[0]
            init_logger_time_format_name = logger_time_format_map.get('logger_time_format_name')
            init_logger_time_format_description = logger_time_format_map.get('logger_time_format_description')
            init_logger_time_ids = logger_time_format_map.get('logger_time_ids')
            init_logger_time_id_types = logger_time_format_map.get('logger_time_id_types')
            init_logger_time_format_form = {
                'logger_time_format_name' : init_logger_time_format_name,
                'logger_time_format_description' : init_logger_time_format_description,
            }
        else:
            print("Couldn't load logger time format from database!")
    else:   #: Add new logger time format
        init_logger_time_format_form = {}

    form = ManageLoggerTimeFormatForm(
        request.POST or None,
        initial=init_logger_time_format_form,
        init_time_ids=init_logger_time_ids,
        init_time_id_types=init_logger_time_id_types
    )

    if form.is_valid():
        logger_time_format_name = form.cleaned_data['logger_time_format_name']
        logger_time_format_description = form.cleaned_data['logger_time_format_description']
        logger_time_format_ids, logger_time_format_id_types = form.clean_time_ids()

        if not logger_time_format_id:
            logger_time_format_id = uuid.uuid4()
        else:
            logs_by_logger_time_format = Logs_by_logger_time_format.get_logs_by_logger_time_format(
                logger_time_format_id
            )
            for log in logs_by_logger_time_format:
                log_id = log.get('log_id')
                log_time_info_data = Log_time_info_by_log.get_log_time_info(log_id)
                if log_time_info_data:
                    log_time_info_map = log_time_info_data[0]   #: Load info into dict
                    temp_logger_time_ids = log_time_info_map.get('logger_time_ids')
                    temp_log_time_zone = log_time_info_map.get('log_time_zone')
                    try:
                        Log_time_info_by_log(log_id=log_id).delete()
                        Log_time_info_by_log.create(
                            log_id=log_id,
                            logger_time_format_id=logger_time_format_id,
                            logger_time_format_name=logger_time_format_name,
                            logger_time_ids=temp_logger_time_ids,
                            log_time_zone=temp_log_time_zone
                        )
                    except:
                        print("Log time info query failed!")
                else:
                    print("Couldn't load log time info from database!")

            try:
                Logger_time_formats(bucket=0, logger_time_format_id=logger_time_format_id).delete()
                Logger_time_format_by_logger_time_format(logger_time_format_id=logger_time_format_id).delete()
            except:
                print("Delete query failed!")

        Logger_time_formats.create(
            bucket=0,
            logger_time_format_id=logger_time_format_id,
            logger_time_format_name=logger_time_format_name,
            logger_time_format_description=logger_time_format_description
        )
        Logger_time_format_by_logger_time_format.create(
            logger_time_format_id=logger_time_format_id,
            logger_time_format_name=logger_time_format_name,
            logger_time_format_description=logger_time_format_description,
            logger_time_ids=logger_time_format_ids,
            logger_time_id_types=logger_time_format_id_types
        )

        url = reverse('sites:index')

        return HttpResponseRedirect(url)

    context = {
        'logger_time_format_id' : logger_time_format_id,
        'logger_time_format_name' : logger_time_format_name,
        'form' : form
    }

    return render(request, template, context)

def delete_logger_time_format(request):
    params = request.GET
    logger_time_format_id = params.get('logger_time_format_id', '')
    logs_by_logger_time_format = Logs_by_logger_time_format.get_logs_by_logger_time_format(logger_time_format_id)
    for log in logs_by_logger_time_format:
        log_id = log.get('log_id')
        try:
            Logs_by_logger_time_format(logger_time_format_id=logger_time_format_id, log_id=log_id).delete()
            Log_time_info_by_log(log_id=log_id).delete()
            Logger_time_formats(bucket=0, logger_time_format_id=logger_time_format_id).delete()
            Logger_time_format_by_logger_time_format(logger_time_format_id=logger_time_format_id).delete()
        except:
            print("Delete logger time format query failed!")

    url = reverse('sites:index')

    return HttpResponseRedirect(url)