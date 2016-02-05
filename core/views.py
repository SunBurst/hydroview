from django.shortcuts import render

import json

from sites.models import Locations, Sensors_by_location, Readings_by_sensor, Sensor_status_by_location

# Create your views here.

def dashboard(request):#request, chartID = 'chart_ID', chart_type = 'line', chart_height = 400):
    template = 'core/dashboard.html'
    #status_data = ChartData.get_status_data()
    #print(status_data)

    #chart = {"renderTo": chartID, "type": chart_type, "zoomType": 'x', "height": chart_height,}
    #title = {"text": 'Battery Status'}
    #xAxis = {"title": {"text": 'Time (Local)'}, "type": 'datetime'}
    #yAxis = {"title": {"text": 'Battery (V)'}}
    #series = status_data#[{
        #'name' : status_data['location'],
        #'data': test
        #}]

    #context = {'locations_list': sites}
    #render(request, template, context)
    #print(template, chartID, chart, series, title, xAxis, yAxis)
    #return render(request, template, {'chartID': chartID, 'chart': chart,
    #                                                'series': series, 'title': title,
    #                                                'xAxis': xAxis, 'yAxis': yAxis})
    return render(request, template)