
var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var epsgsrc = 'EPSG:3857';
var espgdest = 'EPSG:4326';
var geoJSONFormat = new ol.format.GeoJSON();
var wktFormat = new ol.format.WKT();

function getModal(id, config) {
    var element = document.getElementById(id);
    return element ? bootstrap.Modal.getOrCreateInstance(element, config || {}) : null;
}

function showModal(id) {
    var instance = getModal(id);
    if (instance) {
        instance.show();
    }
}

function hideModal(id) {
    var element = document.getElementById(id);
    var instance = element ? bootstrap.Modal.getInstance(element) : null;
    if (instance) {
        instance.hide();
    }
}

function showReturnModal(html) {
    var text = document.getElementById('returnText');
    if (!text) {
        return;
    }
    text.innerHTML = html;
    showModal('returnModal');
}

function escapeHtml(value) {
    var entities = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};
    return String(value).replace(/[&<>"']/g, function (character) {
        return entities[character];
    });
}

function errorMessage(xhr) {
    if (xhr && xhr.responseJSON && typeof xhr.responseJSON === 'object') {
        var data = xhr.responseJSON;
        if (data.result || data.detail) {
            return data.result || data.detail;
        }
        if (typeof data === 'object') {
            var messages = [];
            Object.keys(data).forEach(function (key) {
                var value = data[key];
                messages.push(key + ': ' + (Array.isArray(value) ? value.join(' ') : value));
            });
            if (messages.length) {
                return messages.join(' ');
            }
        }
        return JSON.stringify(data);
    }
    if (xhr && xhr.responseText && !/^\s*</.test(xhr.responseText)) {
        return xhr.responseText;
    }
    if (xhr && xhr.status) {
        return 'HTTP ' + xhr.status;
    }
    return 'Unknown error';
}

function resetForm(id) {
    var form = document.getElementById(id);
    if (form) {
        form.reset();
    }
}

function serializeForm(selector) {
    var out = {};
    $.each($(selector).serializeArray(), function (index, field) {
        out[field.name] = field.value;
    });
    return out;
}

function geometryToField(geometry) {
    var wgsGeometry = geometry.clone().transform(epsgsrc, espgdest);
    return 'SRID=4326;' + wktFormat.writeGeometry(wgsGeometry);
}

function selectionStyle(label) {
    return new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(102, 51, 153, 0.5)',
        }),
        stroke: new ol.style.Stroke({
            color: '#4b0082',
            width: 3,
        }),
        text: new ol.style.Text({
            font: '12px Calibri,sans-serif',
            text: label || '',
            fill: new ol.style.Fill({
                color: '#000',
            }),
            stroke: new ol.style.Stroke({
                color: '#fff',
                width: 3,
            }),
        }),
    });
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
osmlayer.getSource().setTileLoadFunction(function tileLoader(tile, src) {
  var client = new XMLHttpRequest();
  client.open("GET", src);
  client.responseType = "arraybuffer";
  client.setRequestHeader("Accept", "image/*");
  client.setRequestHeader("Content-Type", "text/plain");
  client.setRequestHeader("X-Requested-With", "CASAS Web Portal");
  client.onload = function () {
    var blob = new Blob([this.response], {type: "image/png"});
    var imageUrl = window.URL.createObjectURL(blob);
    tile.getImage().src = imageUrl;
  };
  client.send();
});

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
    name: 'selected',
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
areavector.setVisible(window.user_authenticated !== false);

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
    name: 'drawn',
});


var overlay = new ol.Overlay({
  element: container,
  autoPan: {
    margin: 30,
    animation: {
      duration: 250,
    },
  },
});

var map = new ol.Map({
  target: 'map',
  layers: [osmlayer, sentinellayer, boundsvector, polyvector, areavector, bobavector],
  view: new ol.View({
    center: ol.proj.fromLonLat([20, 10]),
    zoom: 2
  }),
  overlays: [overlay]
});

$('input[name="baselayer"]').on('change', function () {
  var showOsm = this.value == 'osm';
  osmlayer.setVisible(showOsm);
  sentinellayer.setVisible(!showOsm);
})

$('input[name="overlay"]').on('change', function () {
  if (this.value == 'boundaries') {
    boundsvector.setVisible(this.checked);
    if (this.checked) {
      areavector.setVisible(false);
      $('#checkareas').prop('checked', false);
    }
  } else if (this.value == 'myareas') {
    areavector.setVisible(this.checked);
    if (this.checked) {
      boundsvector.setVisible(false);
      $('#checkbounds').prop('checked', false);
    }
  }
})

var hovered = null;
var selectedFeature = null;

function hidePopup() {
    overlay.setPosition(undefined);
}

function clearSelection() {
    bobasource.clear();
    selectedFeature = null;
    hidePopup();
}

var draw = null;
var snap = null;
var drawingActive = false;

function setDrawingState(active) {
    drawingActive = active;
    $('#addselectedfeature').prop('disabled', active);
    if (active) {
        clearSelection();
        clearHover();
    }
}

function removeInteractions() {
    if (draw) {
        map.removeInteraction(draw);
        draw = null;
    }
    if (snap) {
        map.removeInteraction(snap);
        snap = null;
    }
    setDrawingState(false);
    polysource.clear();
    $('#id_geom').val('');
}

function stopDrawing() {
    removeInteractions();
    $('#addarea').removeClass('active').attr('aria-pressed', 'false');
}

function addInteractions() {
    removeInteractions();
    setDrawingState(true);
    $('#areaSelect').val('noarea');
    draw = new ol.interaction.Draw({
        source: polysource,
        type: 'Polygon',
    });
    draw.on('drawend', function (event) {
        var feat = event.feature;
        if (feat.getGeometry().getArea() < 20000000) {
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> The area is too small, please draw a bigger area</i>');
            setTimeout(function () {
                polysource.clear();
            }, 0);
            return;
        }
        $('#drawModalLabel').text('Digitized feature');
        $('#id_geom').val(geometryToField(feat.getGeometry()));
        showModal('drawModal');
    });
    map.addInteraction(draw);
    snap = new ol.interaction.Snap({source: polysource});
    map.addInteraction(snap);
}

$('#addarea').on('click', function () {
    var activate = !$(this).hasClass('active');
    $(this).toggleClass('active', activate);
    $(this).attr('aria-pressed', activate ? 'true' : 'false');
    if (activate) {
        addInteractions();
        showModal('startDrawModal');
    } else {
        removeInteractions();
    }
})

$('#addlayerbtn').on('click', function () {
    stopDrawing();
})

$('#addselectedfeature').on('click', function () {
    if (drawingActive) {
        showReturnModal('<i class="fa-solid fa-circle-exclamation"> Please stop the area drawing tool before selecting a feature</i>');
        return;
    }
    if (!selectedFeature) {
        showReturnModal('<i class="fa-solid fa-circle-exclamation"> Please select a feature on the map first</i>');
        return;
    }
    $('#drawModalLabel').text('Selected world feature');
    $('#id_geom').val(geometryToField(selectedFeature.getGeometry()));
    showModal('drawModal');
})

if (closer) {
    closer.addEventListener('click', function (event) {
        event.preventDefault();
        hidePopup();
    });
}

function clearHover() {
    if (hovered !== null) {
        hovered.setStyle(undefined);
        hovered = null;
        map.getTargetElement().style.cursor = '';
    }
}

map.on('pointermove', function (e) {
  clearHover();
  if (e.dragging || drawingActive) {
    return;
  }
  var hit = map.forEachFeatureAtPixel(e.pixel, function (f, l) {
    return {feature: f, layer: l};
  });
  if (!hit || !hit.layer) {
    return;
  }
  var layerName = hit.layer.get('name');
  var style = null;
  if (layerName == 'areas') {
    style = areahighlight;
  } else if (layerName == 'bounds') {
    style = boundhighlight;
  }
  if (style === null) {
    return;
  }
  hovered = hit.feature;
  style.getText().setText(hovered.get('name') || '');
  hovered.setStyle(style);
  map.getTargetElement().style.cursor = 'pointer';
})

function selectFeature(feature) {
    bobasource.clear();
    var label = feature.get('name') || '';
    var selected = new ol.Feature({
        geometry: feature.getGeometry().clone(),
        name: feature.get('name'),
        id: feature.get('id'),
    });
    if (feature.getId() !== undefined) {
        selected.setId(feature.getId());
    }
    selected.setStyle(selectionStyle(label));
    bobasource.addFeature(selected);
    selectedFeature = selected;
}

function showPopup(label, coordinate) {
    content.innerHTML = '';
    var title = document.createElement('h5');
    title.textContent = label;
    content.appendChild(title);
    overlay.setPosition(coordinate);
}

map.on('click', function (e) {
  if (drawingActive) {
    return;
  }
  var hit = map.forEachFeatureAtPixel(e.pixel, function (f, l) {
    return {feature: f, layer: l};
  });
  if (!hit) {
    clearSelection();
    return;
  }
  var feature = hit.feature;
  var layer = hit.layer;
  var layerName = layer ? layer.get('name') : '';

  if (layerName == 'areas') {
    hidePopup();
    $('#areaSelect').val(feature.get('id'));
    loadArea();
    return;
  }

  if (layer === polyvector) {
    hidePopup();
    $('#drawModalLabel').text('Digitized feature');
    $('#id_geom').val(geometryToField(feature.getGeometry()));
    showModal('drawModal');
    return;
  }

  if (layerName == 'bounds' || layerName == 'selected') {
    if (layerName == 'bounds') {
      selectFeature(feature);
    }
    var label = feature.get('name') || 'Selected feature';
    showPopup(label, e.coordinate);
    $('#id_geom').val(geometryToField(feature.getGeometry()));
    map.getView().fit(feature.getGeometry().getExtent(), {
      size: map.getSize(),
      padding: [40, 40, 40, 40],
    });
    return;
  }

  clearSelection();
})

var file;

function readFile(input) {
    file = input.files[0];
}

$(document).ready(function() {
    var headers = {};
    if (window.drf_token) {
        headers['Authorization'] = 'Token ' + window.drf_token;
    }

    window.addFeature = function() {
        var out = serializeForm('#addFeatureForm');
        if (!out['geom']) {
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> Please digitize an area or select a feature on the map before loading the data</i>');
            return;
        }
        $.ajax({
            type: "POST",
            url: "/api/v1/jobs/",
            headers: headers,
            data: out,
        }).done(function( msg ) {
            hideModal("drawModal");
            showReturnModal('<i class="fa-solid fa-circle-check"> Data uploaded correctly</i>');
            clearSelection();
            stopDrawing();
            resetForm('addFeatureForm');
            getJobs(msg['id']);
        }).fail(function ( msg ) {
            hideModal("drawModal");
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> Data are not uploaded correctly, please try again</i><br><p>' + escapeHtml(errorMessage(msg)) + '</p>');
            getJobs();
        });
    }

    window.addLayer = function() {
      if (!file) {
        showReturnModal('<i class="fa-solid fa-circle-exclamation"> Please select a KML or GeoJSON file before loading the data</i>');
        return;
      }
      var out = serializeForm('#addLayerForm');
      var reader = new FileReader();
      reader.onerror = function () {
        showReturnModal('<i class="fa-solid fa-circle-exclamation"> The selected file could not be read</i>');
      };
      reader.onload = function(event) {
        var format = /\.kml$/i.test(file.name) ? new ol.format.KML() : geoJSONFormat;
        var features;
        try {
            features = format.readFeatures(event.target.result);
        } catch (err) {
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> The selected file could not be read: ' + escapeHtml(err.message) + '</i>');
            return;
        }
        if (!features.length) {
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> No feature has been found in the selected file</i>');
            return;
        }
        out["geom"] = 'SRID=4326;' + wktFormat.writeGeometry(features[0].getGeometry().clone());
        $.ajax({
            type: "POST",
            url: "/api/v1/jobs/",
            headers: headers,
            data: out,
        }).done(function( msg ) {
            hideModal("addLayer");
            showReturnModal('<i class="fa-solid fa-circle-check"> ' + escapeHtml(msg['result'] || 'Data uploaded correctly') + '</i>');
            resetForm('addLayerForm');
            file = undefined;
            getJobs(msg['id']);
        }).fail(function ( msg ) {
            hideModal("addLayer");
            showReturnModal('<i class="fa-solid fa-circle-exclamation"> Data are not uploaded correctly, please try again</i><br><p>' + escapeHtml(errorMessage(msg)) + '</p>');
            getJobs();
        });
      };
      reader.readAsText(file, 'UTF-8');
    }

    window.getJobs = function( myid ) {
    $.ajax({
        type: "GET",
        url: "/api/v1/jobs/",
        headers: headers,
    }).done(function( msg ) {
        var select = $('#areaSelect');
        select.find('option').remove();
        select.append($('<option>').attr('id', 'noarea').val('noarea').text('Select an area'));
        areasource.clear()
        for (var i=0; i<msg.length; i++) {
            var job = msg[i];
            var jobname = job['name']+ ", " + job["model"] + ", " + job["weather"] + ", " + job["start_date"] + "/" + job["end_date"]
            var option = $('<option>')
                .val(job['id'])
                .attr('data-geom', job['geom'])
                .addClass('areatoselect')
                .text(jobname);
            if (String(job['id']) === String(myid)) {
                option.prop('selected', true);
            }
            select.append(option);
            var geomParts = String(job['geom'] || '').split(";");
            try {
                var geom = wktFormat.readGeometry(geomParts.length > 1 ? geomParts[1] : geomParts[0]).transform(espgdest,epsgsrc)
                var newfeat = new ol.Feature({geometry: geom, name: jobname, id: job['id']})
                newfeat.setId(job['id'])
                areasource.addFeature(newfeat);
            } catch (err) {
                console.log('Could not draw the area of job ' + job['id'], err);
            }
        }
    }).fail(function ( msg ) {
        showReturnModal('<i class="fa-solid fa-circle-exclamation"> The list of areas could not be loaded</i><br><p>' + escapeHtml(errorMessage(msg)) + '</p>');
    })
    }

    window.deleteJobs = function(taskid) {
    $.ajax({
        type: "DELETE",
        url: "/api/v1/jobs/" + taskid
    }).done(function( msg ) {
        showReturnModal(escapeHtml((msg && msg['result']) || 'The area has been deleted'));
    }).fail(function (msg) {
        showReturnModal(escapeHtml(errorMessage(msg)));
    })
    }
    window.loadArea = function() {
        var selectedArea = $('#areaSelect').val();
        if (!selectedArea || selectedArea == "noarea") {
            showReturnModal("Please select an area to view");
            return;
        }
        window.location.href = "/job/" + selectedArea;
    }

    getJobs();
});
