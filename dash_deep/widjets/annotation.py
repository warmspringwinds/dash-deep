from dash_deep.app import app, scripts_db_models

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

import numpy as np
import json
import copy

from PIL import Image

from dash_deep.utils import convert_numpy_to_base64_image_string, convert_base64_image_string_to_numpy
from time import sleep

from dash_deep.widjets.widjets_factory import generate_dataset_management_widjet

sql_model = scripts_db_models[1]

layout = generate_dataset_management_widjet(sql_model)