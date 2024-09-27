import json
from pathlib import Path
import pandas as pd
from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import Sweml as app

# functions to load AWS data
import boto3
from botocore import UNSIGNED 
from botocore.client import Config
import os
os.environ['AWS_NO_SIGN_REQUEST'] = 'YES'

# Set Global Variables

try:
    ACCESS_KEY_ID = app.get_custom_setting('Access_key_ID')
    ACCESS_KEY_SECRET = app.get_custom_setting('Secret_access_key')
except Exception:
    ACCESS_KEY_ID = ''
    ACCESS_KEY_SECRET = ''

# AWS Data Connectivity
# start session
SESSION = boto3.Session(
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=ACCESS_KEY_SECRET
)
s3 = SESSION.resource('s3')

BUCKET_NAME = 'national-snow-model'
BUCKET = s3.Bucket(BUCKET_NAME) 
S3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))

# Controller base configurations
basemaps = [
        {'ESRI': {'layer':'NatGeo_World_Map'}},
        {'ESRI': {'layer':'World_Street_Map'}},
        {'ESRI': {'layer':'World_Imagery'}},
        {'ESRI': {'layer':'World_Shaded_Relief'}},
        {'ESRI': {'layer':'World_Topo_Map'}},
        'OpenStreetMap',      
    ]
max_zoom = 16
min_zoom = 1

MODEL_OUTPUT_FOLDER_NAME = 'swe'

@controller(name="home", app_workspace=True)
class swe(MapLayout):
    app = app
    base_template = 'sweml/base.html'
    map_title = 'SWE'
    map_subtitle = 'SWE 1-km Predictions'
    basemaps = basemaps
    max_zoom = max_zoom
    min_zoom = min_zoom
    show_properties_popup = True
    plot_slide_sheet = True

    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        # Load GeoJSON from files
        config_directory = Path(app_workspace.path) / MODEL_OUTPUT_FOLDER_NAME / 'geojson'

        # Nexus Points
        swe_path = config_directory / 'SWE_2024-07-12.geojson'
        with open(swe_path) as nf:
            swe_geojson = json.loads(nf.read())

        swe_layer = self.build_geojson_layer(
            geojson=swe_geojson,
            layer_name='SWE',
            layer_title='SWE 1-km',
            layer_variable='swe',
            visible=True,
            selectable=True,
            plottable=True,
        )

        # Create layer groups
        layer_groups = [
            self.build_layer_group(
                id='sweml',
                display_name='SWE 1-km',
                layer_control='checkbox',  # 'checkbox' or 'radio'
                layers=[
                    swe_layer,
                ]
            )
        ]

        return layer_groups

    @classmethod
    def get_vector_style_map(cls):
        return {
            'Polygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': 'navy',
                    'width': 3
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(0, 25, 128, 0.1)'
                }}
            }},
        }

    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, app_workspace,
                                   *args, **kwargs):
        """
        Retrieves plot data for given feature on given layer.

        Args:
            layer_name (str): Name/id of layer.
            feature_id (str): ID of feature.
            layer_data (dict): The MVLayer.data dictionary.
            feature_props (dict): The properties of the selected feature.

        Returns:
            str, list<dict>, dict: plot title, data series, and layout options, respectively.
        """
        output_directory = Path(app_workspace.path) / MODEL_OUTPUT_FOLDER_NAME / 'geojson'

        # Get the feature id
        x = feature_props.get('x')
        y = feature_props.get('y')

        # Nexus
        if layer_name == 'SWE':
            layout = {
                'yaxis': {
                    'title': 'SWE 1-km'
                }
            }

            output_path = output_directory / f'swe_{x:.2f}_{y:.2f}.csv'
            if not output_path.exists():
                print(f'WARNING: no such file {output_path}')
                return f'No Data Found for SWE at X: {x:.2f} Y: {y:.2f}', [], layout

            # Parse with Pandas
            df = pd.read_csv(output_path)
            time_col = df.iloc[:, 0]
            swe_col = df.iloc[:, 1]
            data = [
                {
                    'name': 'SWE',
                    'mode': 'lines',
                    'x': time_col.tolist(),
                    'y': swe_col.tolist(),
                    'line': {
                        'width': 2,
                        'color': 'blue'
                    }
                },
            ]

            return f'SWE at X: {x:.2f} Y: {y:.2f}', data, layout
