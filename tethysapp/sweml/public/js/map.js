let opacity = 0.8;

const color_dict = {
    0: 'rgba(0, 0, 0, 0)',
    3: `rgba(248, 248, 248, ${opacity})`,
    6: `rgba(221, 221, 248, ${opacity})`,
    9: `rgba(194, 194, 248, ${opacity})`,
    12: `rgba(167, 167, 248, ${opacity})`,
    15: `rgba(140, 140, 248, ${opacity})`,
    18: `rgba(113, 113, 248, ${opacity})`,
    21: `rgba(86, 86, 248, ${opacity})`,
    24: `rgba(59, 59, 248, ${opacity})`,
    27: `rgba(30, 30, 248, ${opacity})`,
    30: `rgba(0, 0, 248, ${opacity})`,
    33: `rgba(81, 40, 137, ${opacity})`,
    36: `rgba(100, 45, 144, ${opacity})`,
    39: `rgba(119, 51, 151, ${opacity})`,
    42: `rgba(139, 56, 159, ${opacity})`,
    45: `rgba(158, 62, 166, ${opacity})`,
    48: `rgba(177, 67, 173, ${opacity})`,
    51: `rgba(197, 73, 181, ${opacity})`,
    54: `rgba(216, 78, 188, ${opacity})`,
    57: `rgba(235, 84, 195, ${opacity})`,
    60: `rgba(255, 90, 204, ${opacity})`
};



function setFeatureColor(feature) {
    
    let swe = feature.get('SWE');

    let key = Math.floor(swe / 3) * 3 + 3;
    return color_dict[key];
}

function createLegend() {
    // Create legend container
    let legendDiv = document.getElementById('legend');

    // Add title to legend
    let legendTitle = document.createElement('div');
    legendTitle.innerHTML = 'Snow Water Equivalent (SWE)';
    legendTitle.id = 'legend-title';
    legendDiv.appendChild(legendTitle);

    // Create color ramp
    let colorRamp = document.createElement('div');
    colorRamp.id = 'legend-color-ramp';
    colorRamp.style.background = createColorGradient(color_dict);
    legendDiv.appendChild(colorRamp);

    // Create labels container
    let labelsDiv = document.createElement('div');
    labelsDiv.id = 'legend-labels';

    // Create labels
    let labelValues = [0, 10, 20, 30, 40, 50, 60]; // Adjust label positions as needed
    for (let value of labelValues) {
        let label = document.createElement('div');
        label.innerText = `${value} in`;
        labelsDiv.appendChild(label);
    }

    legendDiv.appendChild(labelsDiv);

    // Add legend to the map container
    document.getElementById('map_view').appendChild(legendDiv);
}

function createColorGradient(color_dict) {
    let keys = Object.keys(color_dict).sort((a, b) => a - b);
    let gradientColors = [];

    for (let key of keys) {
        let color = color_dict[key];
        let percentage = (key / 60) * 100; // Assuming max value is 60
        gradientColors.push(`${color} ${percentage}%`);
    }

    // Create linear gradient CSS string
    let gradientString = `linear-gradient(to right, ${gradientColors.join(', ')})`;
    return gradientString;
}
    
function regionSelectionVisibility(){
  console.log("regionSelectionVisibility");
    // Get the selected model ID
    let model_id = document.getElementById("model_id").value;
    let region_id = document.getElementById("region-id-div");
    if (model_id === "SWEML_regionalv1.0"){
        region_id.style.display = "block";
    } else{
        region_id.style.display = "none";
    }
}

const inject_map_data = (layer, metadata) => {
  layer.tethys_legend_title = metadata.legend_title;
  layer.tethys_legend_classes = metadata.legend_classes;
  layer.tethys_legend_extent = metadata.legend_extent;
  layer.tethys_legend_extent_projection = metadata.legend_extent_projection;
  layer.tethys_editable = metadata.editable;
  layer.tethys_data = metadata.data;
};

function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (const c of cookies) {
    const [key, value] = c.trim().split('=');
    if (key === name) return decodeURIComponent(value);
  }
  return null;
}


const csrftoken = getCookie('csrftoken'); // same-origin only

$(function() { 
    createLegend();
});



// document.getElementById('model_id').addEventListener('change', regionSelectionVisibility);



document.getElementById('sweml-form').addEventListener('submit', updateData);

function updateData(event) {
  event.preventDefault();

  // Show loading message
  const loadingDiv = document.querySelector('.loading-text');
  loadingDiv.style.display = 'block';

  const errorDiv = document.querySelector('.error-text');
  errorDiv.style.display = 'none';

  
  let date = document.getElementById("date").value;
  let region_id = document.getElementById("region_id").value;
  let model_id = document.getElementById("model_id").value;

  var data = new URLSearchParams();
  data.append('method', 'update_sweml_data');
  data.append('date', date);
  data.append('region_id', region_id);
  data.append('model_id', model_id);

  fetch('.', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrftoken
    },
    body: data
  })
  .then(resp => resp.ok ? resp.json() : Promise.reject(resp))
  .then(data => {
    
    if (!data.success) {
      console.error('Error in server response:', data);
      errorDiv.style.display = 'block';
      const errorp = document.getElementById('text-error-p');
        errorp.innerHTML = "No data available for the selected date.";
      return;
    }
    var olMap = TETHYS_MAP_VIEW.getMap();
    const mapProj = olMap.getView().getProjection();

    const features = new ol.format.GeoJSON().readFeatures(
        data.geojson,
        { dataProjection: 'EPSG:4326', featureProjection: mapProj }
    );
    const newSource = new ol.source.Vector({ features: features });
    olMap.getLayers().forEach(layer => {

        if (layer instanceof ol.layer.Vector) {

            layer.setSource(newSource);
            inject_map_data(layer, data.metadata);
            var featrs = layer.getSource().getFeatures();
            for (let feature of featrs) {
                let color = setFeatureColor(feature);
                let style = new ol.style.Style({
                    fill: new ol.style.Fill({
                        color: color,
                    }),
                });
                feature.setStyle(style);
            }
            const extent = newSource.getExtent();
            if (!ol.extent.isEmpty(extent)) {
                olMap.getView().fit(extent, { padding: [40, 40, 40, 40], duration: 500 });
            }
        }
        
    });


  })
  .catch(err => console.error('REST call failed:', err))
  .finally(() => {
    // Hide loading message when finished
    loadingDiv.style.display = 'none';
  });
}
