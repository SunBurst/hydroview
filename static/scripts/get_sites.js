$(document).ready(function() {

var jsonUrl = '{% url 'sites/load_sites_data' %}'
var sitesDataUrl = jsonUrl + "?name=load_all_sites";

	function loadSites(sitesDataUrl) {
	$.getJSON(sitesDataUrl,
		function(data) {
			var html = '';
			var len = data.length;
				for (var i = 0; i< len; i++) {
					html += '<li><a href="#"><i class="fa fa-map-marker fa-fw"></i>' + ' ' +  data[i] + '<span class=fa arrow"></span></a>'
						+ '</li>'
			}
			$('#configured').append(html);
	});
}
loadSites(sitesDataUrl);
} );