import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

from dash_deep.app import app, scripts_db_models, db, task_manager

import dash_table_experiments as dt
from dash_deep.sql import generate_table_contents_from_sql_model_class
from dash_deep.utils import convert_base64_image_string_to_numpy, convert_numpy_to_base64_image_string


#script_type_name_id = script_sql_class.title.lower().replace(' ', '_')
#interval_object_name_id = script_type_name_id + '-update-interval'
button_id = 'inference-update-button' #script_type_name_id + '-button'
#graph_id_name = script_type_name_id + '-graph'
data_table_id = 'inference-datatable' #script_type_name_id + '-datatable'
#radio_button_id = script_type_name_id + '-radio-button'

#initial_table_contents = generate_table_contents_from_sql_model_class(script_sql_class)

script_sql_class = scripts_db_models[0]

print(script_sql_class.actions['inference'])

layout = html.Div([

        html.H1('Inference page'),
        dt.DataTable(
                     rows=[{}],#initial_table_contents,
                     id=data_table_id,
                     row_selectable=True,
                     filterable=True,
                     ),
        html.Button('Refresh Table', id=button_id),
        dcc.Upload(
        id='inference-upload',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select a File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    ),
    html.Div(id='inference-output')
])


@app.callback(
Output(data_table_id, 'rows'),
[Input(button_id, 'n_clicks')])
def callback(n_clicks):

    rows = generate_table_contents_from_sql_model_class(script_sql_class)

    return rows


@app.callback(Output('inference-output', 'children'),
              [Input('inference-upload', 'contents'),
               Input(data_table_id, 'rows'),
               Input(data_table_id, 'selected_row_indices')])
def update_output(contents, rows, selected_row_indices):
    
    print('submitted')
    
    selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)
    
    selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))
    
    print(selected_experiment_ids)

    extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()
    
    print(extracted_rows)
    # expunge all the models instances (done)
    map(db.session.expunge, extracted_rows)
    
    row = extracted_rows[0]
    
    if contents is not None:
        
        content_type, content_string = contents.split(',')
        
        if 'image' in content_type:
            
            output_images = [html.Img(src=contents)]
            
            for row in extracted_rows:
            
                img_np = convert_base64_image_string_to_numpy(content_string)

                future_obj = task_manager.process_pool.schedule( script_sql_class.actions['inference'],
                                                                 args=(row, img_np) )

                result_np = future_obj.result()

                results_base64 = convert_numpy_to_base64_image_string(result_np)
                
                output_images.append( html.Img(src=results_base64) )
            
            return html.Div(output_images)

# @app.callback(
# Output(graph_id_name, 'figure'),
# [Input(data_table_id, 'rows'),
#  Input(data_table_id, 'selected_row_indices'),
#  Input(interval_object_name_id, 'n_intervals')])
# def callback(rows, selected_row_indices, n_intervals):

#     print(rows)
#     print(selected_row_indices)

#     if not selected_row_indices:

#         return {'data':[], 'layout':[]}

#     selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)

#     selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))

#     extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()

#     mutual_plot = create_mutual_plot(extracted_rows)

#     return mutual_plot


# @app.callback(
# Output(interval_object_name_id, 'interval'),
# [Input(radio_button_id, 'value')])
# def update_interval(value):

#     return value