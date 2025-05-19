import datetime
import json
from pathlib import Path
import pandas as pd
from tethys_sdk.layouts import MapLayout
from tethys_sdk.routing import controller

from django.http import JsonResponse

from django.utils.safestring import mark_safe
from .app import Sweml as app
import geopandas as gpd
from importlib import resources
# Gizmos
from tethys_sdk.gizmos import DatePicker, SelectInput

# functions to load AWS data
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os
import logging

logging.basicConfig(level=logging.INFO)

BUCKET_NAME = "national-snow-model"

csv_path = resources.files('tethysapp.sweml').joinpath('AWSaccessKeys.csv')

if not os.path.exists(csv_path):
    logging.warning(f"File {csv_path} does not exist. Using environment variables instead.")
    SWEML_AWS_ACCESS_KEY_ID = os.environ.get('SWEML_AWS_ACCESS_KEY_ID')
    SWEML_AWS_SECRET_ACCESS_KEY = os.environ.get('SWEML_AWS_SECRET_ACCESS_KEY')

else:
    logging.warning(f"File {csv_path} exists. Using it to load AWS access keys.")
    ACCESS = pd.read_csv(csv_path)
    SWEML_AWS_ACCESS_KEY_ID = ACCESS['Access key ID'][0]
    SWEML_AWS_SECRET_ACCESS_KEY = ACCESS['Secret access key'][0]


SESSION = boto3.Session(
    aws_access_key_id = SWEML_AWS_ACCESS_KEY_ID,
    aws_secret_access_key = SWEML_AWS_SECRET_ACCESS_KEY,
)

s3 = SESSION.resource('s3')

# Controller base configurations
basemaps = [
    {"ESRI": {"layer": "NatGeo_World_Map"}},
    {"ESRI": {"layer": "World_Street_Map"}},
    {"ESRI": {"layer": "World_Imagery"}},
    {"ESRI": {"layer": "World_Shaded_Relief"}},
    {"ESRI": {"layer": "World_Topo_Map"}},
    "OpenStreetMap",
]
max_zoom = 16
min_zoom = 1

MODEL_OUTPUT_FOLDER_NAME = "swe"


@controller(name="sweml", app_workspace=True)
class swe(MapLayout):
    app = app
    base_template = "sweml/base.html"
    map_title = "SWE"
    map_subtitle = "SWE 1-km Predictions"
    basemaps = basemaps
    max_zoom = max_zoom
    min_zoom = min_zoom
    show_properties_popup = True
    plot_slide_sheet = True
    template_name = "sweml/swe.html"

    def get_context(self, request, *args, **kwargs):
        """
        Create context for the Map Layout view, with an override for the map extents based on date.

        Args:
            request (HttpRequest): The request.
            context (dict): The context dictionary.

        Returns:
            dict: modified context dictionary.
        """

        initial_date = datetime.datetime.today().strftime('%Y-%m-%d')

        date_picker = DatePicker(
            name="date",
            display_text="Date",
            autoclose=False,
            format="yyyy-mm-dd",
            start_date="2015-10-01",
            end_date="today",
            start_view="year",
            today_button=False,
            initial=initial_date,
        )

        model_id = SelectInput(
            display_text='Select Model',
            name='model_id',
            multiple=False,
            options=[
                ('National Snow Model v1.0', 'SWEMLv1.0'),
                ('Regional Snow Model v1.0', 'SWEML_regionalv1.0'),
            ],
            initial=['National Snow Model v1.0'],
            select2_options={
                'placeholder': 'Select a model',
                'allowClear': True
            },
            attributes={"onchange": "regionSelectionVisibility();", "id": "model_id"}
        )

        region_id = SelectInput(
            display_text='Select Region',
            name='region_id',
            multiple=False,
            options=[('Tuolumne Basin', 'Tuolumne_Basin'),
                     ('Upper Colorado River Basin', 'UCRB')],
            initial=['Tuolumne Basin'],
            select2_options={
                'placeholder': 'Select a region',
                'allowClear': True
            },
        )

        # Call Super
        context = super().get_context(request, *args, **kwargs)

        context["date_picker"] = date_picker
        context['model_id'] = model_id
        context['region_id'] = region_id

        return context

    def compose_layers(self, request, map_view, app_workspace, *args, **kwargs):
        """
        Add layers to the MapLayout and create associated layer group objects.
        """
        # http request for user inputs
        model_id = request.GET.get("model_id", "SWEMLv1.0")
        region_id=request.GET.get("region_id","Tuolumne Basin")
        date = request.GET.get("date",datetime.datetime.today().strftime('%Y-%m-%d') )

        layer_name = "SWE"
        layer_title = "SWE"

        # set AWS path for GeoJSON files
        if model_id == "SWEMLv1.0":
            s3_geojson_directory = "Neural_Network/Hold_Out_Year/Daily/GeoJSON"
            # layer_title = "SWE"
        else:
            if int(date[5:7]) < 10:
                year = int(date[0:4]) - 1
            else:
                year = date[0:4]
            s3_geojson_directory = f"SWEMLv1Regional/{region_id}/{year}/Data/GeoJSON"
            layer_title = f"SWE_{region_id}"
        
        try:
            file = f"SWE_{date}.geojson"
            file_path = f"{s3_geojson_directory}/{file}"


            file_object = s3.Object(BUCKET_NAME, file_path)
            file_content = file_object.get()["Body"].read().decode("utf-8")
            swe_geojson = json.loads(file_content)

            # this is to get the rounded SWE values
            gdf = gpd.GeoDataFrame.from_features(swe_geojson["features"])
            gdf["SWE"] = gdf["SWE"].round(3)
            gdf["x"] = gdf["x"].round(3)
            gdf["y"] = gdf["y"].round(3)

            # convert back to geojson
            swe_geojson = json.loads(gdf.to_json())
            
            swe_layer = self.build_geojson_layer(
                geojson=swe_geojson,
                layer_name=layer_name,
                layer_title=layer_title,
                layer_variable="swe",
                visible=True,
                selectable=True,
                plottable=True,
                show_legend=True,
            )

            # Create layer groups
            layer_groups = [
                self.build_layer_group(
                    id="sweml",
                    display_name="SWE 1-km",
                    layer_control="checkbox",  # 'checkbox' or 'radio'
                    layers=[
                        swe_layer,
                    ],
                )
            ]
        

        except:
            layer_name = "SWE"
            swe_geojson = {
                "type": "FeatureCollection",
                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                "features": []
            }
            swe_layer = self.build_geojson_layer(
                geojson=swe_geojson,
                layer_name=layer_name,
                layer_title=layer_title,
                layer_variable="swe",
                visible=True,
                selectable=True,
                plottable=True,
                show_legend=True,
            )
            # Create layer groups
            layer_groups = [
                self.build_layer_group(
                    id="sweml",
                    display_name="SWE 1-km",
                    layer_control="checkbox",  # 'checkbox' or 'radio'
                    layers=[
                        swe_layer,
                    ],
                )
            ]

        return layer_groups

    @classmethod
    def get_vector_style_map(cls):
        return {
            "Polygon": {
                "ol.style.Style": {
                    "stroke": {"ol.style.Stroke": {"color": "navy", "width": 3}},
                    "fill": {"ol.style.Fill": {"color": "rgba(0, 25, 128, 0.1)"}},
                }
            },
        }

    def get_plot_for_layer_feature(self, request, layer_name, feature_id, layer_data, feature_props, app_workspace,
                                   *args, **kwargs, ):
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
        x = feature_props.get("x")
        y = feature_props.get("y")

        date = datetime.datetime.strptime(request.session['date'], "%Y-%m-%d")
        if date.month >= 10:
            start_date = pd.to_datetime(datetime.date(date.year, 10, 1))
            end_date = pd.to_datetime(datetime.date(date.year + 1, 9, 30))
        else:
            start_date = pd.to_datetime(datetime.date(date.year - 1, 10, 1))
            end_date = pd.to_datetime(datetime.date(date.year, 9, 30))

        # SWE
        if "SWE" in layer_name:
            layout = {"yaxis": {"title": "SWE 1-km in inches"}}

            # S3 path for csv files
            if layer_name == "SWE":
                csv_directory = "Neural_Network/Hold_Out_Year/Daily/csv"
            else:
                region_id = request.session['region_id']
                # region_id = layer_name[4:]
                year = start_date.year
                csv_directory = f"SWEMLv1Regional/{region_id}/{year}/Data/csv"

            try:
                file = f"swe_1000m_{y:.3f}_{x:.3f}.csv"
                file_path = f"{csv_directory}/{file}"
                file_object = s3.Object(BUCKET_NAME, file_path)
                file_content = file_object.get()["Body"]

                if not file_content:
                    logging.warning(f"WARNING: no such file {file_path}")
                    return f"No Data Found for SWE at Lat: {y:.3f} Lon: {x:.3f}", [], layout

                # Parse with Pandas


                df = pd.read_csv(file_content)
                
                df.date = pd.to_datetime(df.date)
                if layer_name == "SWE":
                    mask = (df["date"] > start_date) & (df["date"] <= end_date)
                    df = df.loc[mask]
                if df.empty:
                    logging.warning(f"WARNING: no such file {file_path}")
                    return f"No Data Found for SWE at Lat: {y:.3f} Lon: {x:.3f}", [], layout
                time_col = df.iloc[:, 0]
                swe_col = df.iloc[:, 1]
                data = [
                    {
                        "name": "SWE",
                        "mode": "lines",
                        "x": time_col.tolist(),
                        "y": swe_col.tolist(),
                        "line": {"width": 2, "color": "blue"},
                    },
                ]
                return f"SWE at Lat: {y:.3f} Lon: {x:.3f}", data, layout
            
            except pd.errors.EmptyDataError:
                logging.warning(f"WARNING: no such file {file_path}")
                return f"No Data Found for SWE at Lat: {y:.3f} Lon: {x:.3f}", [], layout
            except Exception as e:
                print(f"WARNING: no such file {file_path}")
                print(e)
                return f"No Data Found for SWE at Lat: {y:.3f} Lon: {x:.3f}", [], layout

    def update_sweml_data(self, request, *args, **kwargs):
        
        data = request.POST or request.json()
        request.session['model_id'] = data.get('model_id')
        request.session['date'] = data.get('date', datetime.datetime.today().strftime('%Y-%m-%d'))
        request.session['region_id'] = data.get('region_id')

        model_id = request.session['model_id']
        date =  request.session['date']
        layer_name = "SWE"

        # set AWS path for GeoJSON files
        if model_id == "SWEMLv1.0":
            s3_geojson_directory = "Neural_Network/Hold_Out_Year/Daily/GeoJSON"
        else:
            if int(date[5:7]) < 10:
                year = int(date[0:4]) - 1
            else:
                year = date[0:4]
            region_id = request.session['region_id']
            s3_geojson_directory = f"SWEMLv1Regional/{region_id}/{year}/Data/GeoJSON"
            # layer_name = f"SWE_{region_id}"

        try:
            
            file = f"SWE_{date}.geojson"
            file_path = f"{s3_geojson_directory}/{file}"
            file_object = s3.Object(BUCKET_NAME, file_path)
            file_content = file_object.get()["Body"].read().decode("utf-8")
            swe_geojson = json.loads(file_content)

            # this is to get the rounded SWE values
            gdf = gpd.GeoDataFrame.from_features(swe_geojson["features"])
            gdf["SWE"] = gdf["SWE"].round(3)
            gdf["x"] = gdf["x"].round(3)
            gdf["y"] = gdf["y"].round(3)

            # convert back to geojson
            swe_geojson = json.loads(gdf.to_json())

            swe_layer = self.build_geojson_layer(
                geojson=swe_geojson,
                layer_name=layer_name,
                layer_title=layer_name,
                layer_variable="swe",
                visible=True,
                selectable=True,
                plottable=True,
                show_legend=True,
            )

            return JsonResponse({'success': True,'metadata': swe_layer ,'geojson': swe_geojson})

        except:
            layer_name = "SWE"            
            swe_geojson = {
                "type": "FeatureCollection",
                "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
                "features": []
            }
            swe_layer = self.build_geojson_layer(
                geojson=swe_geojson,
                layer_name=layer_name,
                layer_title=layer_name,
                layer_variable="swe",
                visible=True,
                selectable=True,
                plottable=True,
                show_legend=True,
            )
     
            return JsonResponse({'success': False,'metadata': swe_layer ,'geojson': swe_geojson})

        