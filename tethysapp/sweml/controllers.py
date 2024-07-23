import json
from pathlib import Path

from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import Sweml as app

#functions to load AWS data
import boto3
import os
from botocore import UNSIGNED 
from botocore.client import Config
import os
os.environ['AWS_NO_SIGN_REQUEST'] = 'YES'

#Set Global Variables

try:
    ACCESS_KEY_ID = app.get_custom_setting('Access_key_ID')
    ACCESS_KEY_SECRET = app.get_custom_setting('Secret_access_key')
except Exception:
    ACCESS_KEY_ID = ''
    ACCESS_KEY_SECRET = ''

#AWS Data Connectivity
#start session
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


@controller(name="home", app_workspace=True)
class swe(MapLayout):
    app = app
    base_template = 'sweml/base.html'
    map_title = 'SWE'
    map_subtitle = 'SWE 1-km Predictions'
    basemaps = basemaps
    max_zoom = max_zoom
    min_zoom = min_zoom

    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        # Load GeoJSON from files
        config_directory = Path(app_workspace.path) / 'sweml' / 'geojson'

        # Nexus Points
        swe_path = config_directory / 'SWE_2022-10-08.geojson'
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