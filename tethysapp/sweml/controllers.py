import json
from pathlib import Path
import pandas as pd
from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller
from .app import Sweml as app

#Date picker
from tethys_sdk.gizmos import DatePicker

# functions to load AWS data
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os

os.environ['AWS_NO_SIGN_REQUEST'] = 'YES'

# Set Global Variables

BUCKET_NAME = 'national-snow-model'
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))

# Controller base configurations
basemaps = [
    {'ESRI': {'layer': 'NatGeo_World_Map'}},
    {'ESRI': {'layer': 'World_Street_Map'}},
    {'ESRI': {'layer': 'World_Imagery'}},
    {'ESRI': {'layer': 'World_Shaded_Relief'}},
    {'ESRI': {'layer': 'World_Topo_Map'}},
    'OpenStreetMap',
]
max_zoom = 16
min_zoom = 1

MODEL_OUTPUT_FOLDER_NAME = 'swe'


@controller(name="swe",
            url="swe/",
            app_workspace=True)
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
    template_name = 'sweml/swe.html'

    def get_context(self, request, *args, **kwargs):
        """
        Create context for the Map Layout view, with an override for the map extents based on date.

        Args:
            request (HttpRequest): The request.
            context (dict): The context dictionary.

        Returns:
            dict: modified context dictionary.
        """

        date_picker = DatePicker(
            name='date',
            display_text='Date',
            autoclose=False,
            format='yyyy-mm-dd',
            start_date='2023-01-01',
            end_date='2024-12-30',
            start_view='year',
            today_button=False,
            initial='2024-06-15'
        )

        # Call Super
        context = super().get_context(
            request,
            *args,
            **kwargs
        )
        context['date_picker'] = date_picker

        return context

    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        # Load GeoJSON from files
        config_directory = Path(app_workspace.path) / MODEL_OUTPUT_FOLDER_NAME / 'geojson'

        geojson_directory = "Neural_Network/Hold_Out_Year/Daily/GeoJSON"

        try:
            # http request for user inputs
            date = request.GET.get('date')

            file = f'SWE_{date}.geojson'
            file_path = f'{geojson_directory}/{file}'
            file_object = s3.Object(BUCKET_NAME, file_path)
            file_content = file_object.get()['Body'].read().decode('utf-8')
            swe_geojson = json.loads(file_content)

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

        except:
            date = '2024-07-12'

            file = f'SWE_{date}.geojson'

            # Nexus Points
            swe_path = config_directory / file
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

        csv_directory = "Neural_Network/Hold_Out_Year/Daily/csv"

        # Get the feature id
        x = feature_props.get('x')
        y = feature_props.get('y')

        # SWE
        if layer_name == 'SWE':
            layout = {
                'yaxis': {
                    'title': 'SWE 1-km'
                }
            }

            file = f'swe_1000m_{y:.3f}_{x:.3f}.csv'
            file_path = f'{csv_directory}/{file}'
            file_object = s3.Object(BUCKET_NAME, file_path)
            file_content = file_object.get()['Body']

            if not file_content:
                print(f'WARNING: no such file {file_path}')
                return f'No Data Found for SWE at Lat: {y:.3f} Lon: {x:.3f}', [], layout

            # Parse with Pandas
            df = pd.read_csv(file_content)
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

            return f'SWE at Lat: {y:.3f} Lon: {x:.3f}', data, layout
