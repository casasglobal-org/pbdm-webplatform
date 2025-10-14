
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

var boundstyle = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(100, 100, 100, 0.05)',
  }),
  stroke: new ol.style.Stroke({
    color: '#000000',
    width: 1,
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
var boundhighlight = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(100, 100, 100, 0.4)',
  }),
  stroke: new ol.style.Stroke({
    color: '#000000',
    width: 3,
  }),
})

var boundsvector = new ol.layer.Vector({
  source: new ol.source.Vector({
    format: geoJSONFormat,
    url: '/static/data/boundaries.geojson'
  }),
  name: 'bounds',
  style: boundstyle
});
boundsvector.setVisible(false);

var bobastyle = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(102, 51, 153, 0.4)',
  }),
  stroke: new ol.style.Stroke({
    color: '#663399',
    width: 2,
  }),
  image: new ol.style.Circle({
    radius: 7,
    fill: new ol.style.Fill({
      color: '#ffcc33',
    }),
  })
})

var bobasource = new ol.source.Vector();
var bobavector = new ol.layer.Vector({
    source: bobasource,
    style: bobastyle,
    name: 'selected,'
});

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
areavector.setVisible(false);


var polystyle = new ol.style.Style({
  fill: new ol.style.Fill({
    color: 'rgba(255, 0, 0, 0.4)',
  }),
  stroke: new ol.style.Stroke({
    color: '#ff0000',
    width: 2,
  }),
  image: new ol.style.Circle({
    radius: 7,
    fill: new ol.style.Fill({
      color: '#ffcc33',
    }),
  }),
})

var polysource = new ol.source.Vector();
var polyvector = new ol.layer.Vector({
    source: polysource,
    style: polystyle,
    name: 'selected,'
});


var overlay = new ol.Overlay({
  element: container,
  autoPan: true,
  autoPanAnimation: {
    duration: 250,
  },
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
  layers: [osmlayer, sentinellayer, boundsvector, polyvector, areavector, bobavector],
  view: new ol.View({
    center: ol.proj.fromLonLat([20, 10]),
    zoom: 2
  }),
  overlays: [overlay]
  //controls: ol.control.defaults({attribution: false}).extend([attribution])
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

$('input[type="checkbox"]').click(function(){
  if($(this).prop("checked")){
    var layername = $(this).val()
  }
  if (layername == 'myareas'){
    areavector.setVisible(true);
    boundsvector.setVisible(false);
    $('#checkbounds').prop( "checked", false );
  } else {
    areavector.setVisible(false);
  }
  if (layername == 'boundaries'){
    boundsvector.setVisible(true);
    areavector.setVisible(false);
    $('#checkareas').prop( "checked", false );
  } else {
    boundsvector.setVisible(false);
  }
})

var draw, snap; // global so we can remove them later
var typeSelect = document.getElementById('type');
function addInteractions() {
    polysource.clear()
    $('#areaSelect').val('noarea')
    draw = new ol.interaction.Draw({
    source: polysource,
    type: 'Polygon',
    });
    draw.on('drawstart', function (event) {
    event.feature.getGeometry().on('change', function(e){
        window.event = event;
    });
    });
    draw.on('drawend', function (event) {
    var feat = event.feature;
    if (feat.getGeometry().getArea() < 20000000){
        $("#returnText").text("The area is too small, please draw a bigger area");
        $("#returnModal").modal('show');
        polysource.clear();
    //} else if (feat.getGeometry().getArea() > 100000000) {
//            	$("#returnText").text("The area is to big, please draw a bigger area");
//              $("#returnModal").modal('show');
//              polysource.clear();
    } else {
        var wktStr = wktFormat.writeGeometry(feat.getGeometry().transform(epsgsrc, espgdest));
        $("#id_geom").val("SRID=4326;" + wktStr);
        drawModal.show()
    }

    });
    map.addInteraction(draw);
    snap = new ol.interaction.Snap({source: polysource});
    map.addInteraction(snap);
}

$('#addarea').click(function () {
    if($(this).hasClass('active')){
      startDrawModal.show()
      addInteractions();
    } else {
      map.removeInteraction(draw);
      map.removeInteraction(snap);
    }
})
$('#addlayerbtn').click(function () {
    if($(this).hasClass('active')){
    map.removeInteraction(draw);
    map.removeInteraction(snap);
    }
})

var hovered = null;
var newfeat = null;
map.on('pointermove', function (e) {
  if (hovered !== null) {
    hovered.setStyle(undefined);
    hovered = null;
  }

  map.forEachFeatureAtPixel(e.pixel, function (f, l) {
    if(l){
      if (l.get('name') == 'areas'){
        hovered = f;
        f.setStyle(areahighlight);
        f.getStyle().getText().setText(f.get('name'));
        return true;
      } else if (l.get('name') == 'basins') {
        hovered = f;
        f.setStyle(areahighlight);
        f.getStyle().getText().setText(f.get('name'));
        return true;
      } else if (l.get('name') == 'bounds') {
        hovered = f;
        f.setStyle(areahighlight);
        f.getStyle().getText().setText(f.get('name'));
        return true;
      } else {
        var fid = f.getId();
        if (l.get('name') == 'areas'){
          var featstyle = areasource.getFeatureById(fid);
          featstyle.setStyle(areastyle);
          return true;
        } else if (l.get('name') == 'bounds') {
          var featstyle = areasource.getFeatureById(fid);
          featstyle.setStyle(boundstyle);
          return true;
        }
      }
    }
  })
})

map.on('click', function (e) {
  var coordinate = e.coordinate;
  map.forEachFeatureAtPixel(e.pixel, function (f, l) {
    polysource.clear()
    bobasource.clear()
    if (newfeat !== null) {
        var oldid  = newfeat.get('id')
        newfeat.setStyle(undefined);
        newfeat = null
    }
    newfeat = f
    if (l.get('name') == 'areas'){
        $('#areaSelect').val(f.get('id'))
        $('#areaSelect').change();
    } else {
        var contenttext = '<h5>'+ f.get('name') +'</h5>';
        contenttext = contenttext + '<div class="row">'
        contenttext = contenttext + '</div>'
        content.innerHTML = contenttext;

        var ext = newfeat.getGeometry().getExtent();
        bobasource.addFeature(newfeat);
        var center = ol.extent.getCenter(ext);
        map.getView().fit(ext, map.getSize());
        overlay.setPosition(coordinate);
    }
  })
})

var file;

function readFile(input) {
    file = input.files[0];
}

$(document).ready(function() {
    var headers = {'Token': window.drf_token };
    window.addFeature = function() {
        var formData = $("#addFeatureForm").serializeArray();
        out = {};
        for (idd in formData) {
            dat = formData[idd];
            out[dat.name] = dat.value;
        }
        console.log(out);
        $.ajax({
            type: "POST",
            url: "/api/v1/jobs/",
            headers: headers,
            data: out,
        }).done(function( msg ) {
            $("#drawModal").modal('hide');
            $("#returnText").text("");
            $("#returnText").text('<i class="fa-solid fa-circle-check"> Data uploaded correctly</i>')
            $("#returnModal").modal('show');
            addid = msg['featid'];
            getJobs(addid);
        }).fail(function (msg) {
            console.log(msg);
            $("#drawModal").modal('hide');
            $("#returnText").text("");
            $("#returnText").html('<i class="fa-solid fa-circle-exclamation"> Data are not uploaded corretly, please try again</i><br><p>Error: ' + msg.responseText + '</p>');
            $("#returnModal").modal('show');
            getJobs();
        });
    }

    window.addLayer = function() {
      var reader = new FileReader();
      reader.readAsText(file, 'UTF-8');
      reader.onload = shipOff;

      var formData = $("#addLayerForm").serializeArray();
      out = {};
      for (idd in formData) {
        dat = formData[idd];
        out[dat.name] = dat.value;
      }
      function shipOff(event) {
        var result = event.target.result;
        var features = new ol.format.GeoJSON().readFeatures( result );
        console.log(features[0])
        var wktStr = wktFormat.writeGeometry(features[0].getGeometry());
        out["geom"] = 'SRID=4326;' + wktStr
        console.log(out)
        $.ajax({
            type: "POST",
            url: "/api/v1/jobs/",
            headers: headers,
            data: out,
        }).done(function( msg ) {
            $("#addLayer").modal('hide');
            $("#returnText").text("")
            $("#returnText").text(msg['result']);
            $("#returnModal").modal('show');
            getJobs();
        }).fail(function (msg) {
            $("#addLayer").modal('hide');
            $("#returnText").text("");
            $("#returnText").text(msg.responseJSON['result']);
            $("#returnModal").modal('show');
            getJobs();
        });
      }
    }

    window.getJobs = function( myid ) {
    $.ajax({
        type: "GET",
        url: "/api/v1/jobs/",
        headers: headers,
    }).done(function( msg ) {
        $('#areaSelect').find('option').remove().end().append('<option value="noarea" id="noarea">Select an area</option>').val('noarea')
        areasource.clear()
        for (i=0; i<msg.length; i++) {
            jobname = msg[i]['name']+ ", " + msg[i]["model"] + ", " + msg[i]["weather"] + ", " + msg[i]["start_date"] + "/" + msg[i]["end_date"]
            if ( msg[i]['id'] == myid) {
                $('#areaSelect').append("<option selected value=" +
                msg[i]['id'] + " data-geom='" + JSON.stringify(msg[i]['geom']) + "' class='areatoselect'>" +
                jobname + "</option>");
            } else {
                $('#areaSelect').append("<option value=" +
                msg[i]['id'] + " data-geom='" + JSON.stringify(msg[i]['geom']) + "' class='areatoselect'>" +
                jobname + "</option>");
            }
            var geom = wktFormat.readGeometry(msg[i]['geom'].split(";")[1]).transform(espgdest,epsgsrc)
            var newfeat = new ol.Feature({geometry: geom, name: jobname, id: msg[i]['id']})
            newfeat.setId(msg[i]['id'])
            areasource.addFeature(newfeat);
        }
        $('#areaSelect').change();
    }).fail
    }

    window.deleteJobs = function(taskid) {
    $.ajax({
        type: "DELETE",
        url: "/api/v1/jobs/" + taskid
    }).done(function( msg ) {
        $("#returnText").text("");
        $("#returnText").text(msg['result'])
        $("#returnModal").modal('show');
    }).fail(function (msg) {
        $("#returnText").text("");
        $("#returnText").text(msg['result'])
        $("#returnModal").modal('show');
    })
    }

    // window.getTasks = function () {
    // $.ajax({
    //     type: "GET",
    //     url: "/gettasks"
    // }).done(function( msg ) {
    //     $("#previoustasks").text("");
    //     var tasks = '<h5 class="card-title text-center">Previous task succefully finished</h5>'
    //     for (i=0; i<msg['data'].length; i++) {
    //     tasks += '<div class="row"><div class="col-sm-12 col-lg-5">' + msg['data'][i]['fields']['area'] + "<br>" + msg['data'][i]['fields']['data'].replace('T', ' ').split('.', 1) + '</div>' +
    //                 '<div class="col-sm-12 col-lg-7"><a href="/media/' + msg['data'][i]['fields']['task'] + '/index.html" target="_blank" class="btn btn-primary m-1">view</a>' +
    //                 '<a href="/media/' + msg['data'][i]['fields']['task'] + '/report.pdf" target="_blank" class="btn btn-primary m-1">pdf</a>' +
    //                 '<a onclick="deleteTaskhistory(' + msg['data'][i]['id'] + ')" class="btn btn-primary m-1">delete</a></div></div>'
    //     if (i != msg['data'].length - 1) {
    //         tasks += '<hr>';
    //     }
    //     }
    //     $("#previoustasks").append(tasks);
    // })
    // }
    getJobs();
});