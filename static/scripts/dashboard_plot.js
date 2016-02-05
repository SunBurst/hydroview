<script src="{{ STATIC_URL }}scripts/dashboard_plot.js"></script>
$(document).ready(function() {
//    Highcharts.setOptions({
//        global: {
//        useUTC: false
//    }
//});
//    $(chart_id).highcharts({
//        chart: chart,
//        title: title,
//        xAxis: xAxis,
//        yAxis: yAxis,
//        series: series
//    });


    // Battery Status by day chart
     var statusByDayOptions = {
        chart: {
            renderTo: 'chart_panel',
            type: 'line',
        },
        legend: {enabled: false},
        title: {text: 'Battery Status By Day'},
        subtitle: {text: 'placeholder'},
        xAxis: {title: {text: null}, type: 'datetime'},
        yAxis: {title: {text: 'Battery (V)'}},
        series: [{}],
    };

    var chartDataUrl = "{% url 'chart_data_json' %}?name=status_by_day";
        function loadChart() {
        $.getJSON(chartDataUrl,
            function(data) {
                statusByDayOptions.xAxis.categories = [1388703600000, 1388617200000, 1388530800000]//data['chart_data'][0]['time'];
                statusByDayOptions.series[0].name = 'island'//data['chart_data'][0]['location']
                statusByDayOptions.series[0].data = [13.8, 13.5, 13.6]//data['chart_data'][0]['values'];
                var chart = new Highcharts.Chart(statusByDayOptions);
        });
    }

    loadChart();
} );