
var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var epsgsrc = 'EPSG:3857';
var espgdest = 'EPSG:4326';
var geoJSONFormat = new ol.format.GeoJSON({});
var wktFormat = new ol.format.WKT();
if (document.getElementById('drawModal')){
    var drawModal = new bootstrap.Modal(document.getElementById('drawModal'), {
        keyboard: false
    })
}
if (document.getElementById('startDrawModal')){
    var startDrawModal = new bootstrap.Modal(document.getElementById('startDrawModal'), {
        keyboard: false
    })
}

var attribution = new ol.control.Attribution({
  collapsible: false,
});

function checkSize() {
  var small = map.getSize()[0] < 600;
  attribution.setCollapsible(small);
  attribution.setCollapsed(small);
}


var sentinellayer = new ol.layer.Tile({
  source: new ol.source.TileWMS({
    url: 'https://tiles.maps.eox.at/wms?',
    params: {'LAYERS': 's2cloudless_3857'},
    version: '1.1.1',
    format: 'image/png',
    ratio: 1,
    serverType: 'mapserver',
    attributions: ['Sentinel-2 cloudless - <a href="https://s2maps.eu" target="_blank" title="Sentinel-2 cloudless">https://s2maps.eu</a> by <a href="https://eox.at/" target="_blank" title="Eox Company">EOX IT Services GmbH</a> (Contains modified Copernicus Sentinel data 2016 & 2017)']
  }),
  visible: false
})
var osmlayer = new ol.layer.Tile({
  source: new ol.source.OSM()
})

var areastyle = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(255, 255, 0, 0.4)',
  }),
  stroke: new ol.style.Stroke({
    color: '#ffff00',
    width: 2,
  }),
  image: new ol.style.Circle({
    radius: 7,
    fill: new ol.style.Fill({
      color: '#ffcc33',
    }),
  })
})

var areahighlight = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(0, 255, 0, 0.4)',
  }),
  stroke: new ol.style.Stroke({
    color: '#00ff00',
    width: 3,
  }),
  image: new ol.style.Circle({
    radius: 7,
    fill: new ol.style.Fill({
      color: '#ffcc33',
    }),
  }),
  text: new ol.style.Text({
    font: '12px Calibri,sans-serif',
    fill: new ol.style.Fill({
      color: '#000',
    }),
    stroke: new ol.style.Stroke({
        color: '#fff',
        width: 3,
    }),
    }),
})

var areasource = new ol.source.Vector();
var areavector = new ol.layer.Vector({
    source: areasource,
    style: areastyle,
    name: 'areas',
});
areavector.setVisible(true);


var overlay = new ol.Overlay({
  element: container,
  autoPan: true,
  autoPanAnimation: {
    duration: 250,
  },
});

var legendbutton = document.getElementById('legend-button');
var legenddiv = document.getElementById('ol-legend');
var legend = document.getElementById('legend');
legend.style.display = "none";
var showhidelegend = function(e) {
    var legend = document.getElementById('legend');
    if (legend.style.display === "none") {
        legend.style.display = "block";
    } else {
        legend.style.display = "none";
    }
};
legendbutton.addEventListener('click', showhidelegend, false);


var legendControl = new ol.control.Control({
    element: legenddiv
});

var map = new ol.Map({
//   controls: ol.control.defaults().extend(
//   [
//     new ol.control.ScaleLine({
//         bar: false,
//         steps: 4,
//         text: true,
//         minWidth: 100
//     })
//   ]),
  target: 'map',
  layers: [osmlayer, sentinellayer, areavector],
  view: new ol.View({
    center: ol.proj.fromLonLat([20, 10]),
    zoom: 2
  }),
  overlays: [overlay],
  controls: ol.control.defaults.defaults().extend([new ol.control.ZoomToExtent(), legendControl]),
});

$('input[type="radio"]').click(function(){
  if($(this).prop("checked")){
    var layername = $(this).val()
  }
  if (layername == 'osm'){
    sentinellayer.setVisible(false);
    osmlayer.setVisible(true);
  } else if (layername == 'sen2'){
    sentinellayer.setVisible(true);
    osmlayer.setVisible(false);
  }
})

$(document).ready(function() {
    var headers = {'Token': window.drf_token };


    window.getJob = function() {
        areasource.clear();
        var geom_str = document.getElementById("job_geom").value;
        var geom = wktFormat.readGeometry(geom_str.split(";")[1]).transform(espgdest,epsgsrc);
        var name = document.getElementById("job_name").value;
        var myid = document.getElementById("job_id").value;
        var newfeat = new ol.Feature({geometry: geom, name: name, id: myid});
        newfeat.setId(myid);
        areasource.addFeature(newfeat);
        var extent = geom.getExtent();
        map.getView().fit(extent, {size: map.getSize(), maxZoom: 14, duration: 1000});
    }

    getJob();
});