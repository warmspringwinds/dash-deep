import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, Event

from dash_deep.app import app, scripts_db_models, db, task_manager

import dash_table_experiments as dt
from dash_deep.sql import generate_table_contents_from_sql_model_class
from dash_deep.utils import convert_base64_image_string_to_numpy, convert_numpy_to_base64_image_string


script_sql_class = scripts_db_models[0]

script_type_name_id = script_sql_class.title.lower().replace(' ', '_')
button_id = script_type_name_id + '-inference-refresh-button'
data_table_id = script_type_name_id + '-inference-datatable'
upload_widjet_id = script_type_name_id + '-inference-upload'
output_div_id = script_type_name_id + '-inference-output-results'

layout = html.Div([

        html.H1(script_sql_class.title),
        dt.DataTable(
                     rows=[{}],
                     id=data_table_id,
                     row_selectable=True,
                     filterable=True,
                     ),
        html.Button('Refresh Table', id=button_id),
        dcc.Upload(
        id=upload_widjet_id,
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
        },
       multiple=True
    ),
    html.Div(id=output_div_id)
])


@app.callback(
Output(data_table_id, 'rows'),
[Input(button_id, 'n_clicks')])
def callback(n_clicks):

    rows = generate_table_contents_from_sql_model_class(script_sql_class)

    return rows


@app.callback(Output(output_div_id, 'children'),
              [Input(upload_widjet_id, 'contents'),
               Input(upload_widjet_id, 'filename'),
               Input(data_table_id, 'rows'),
               Input(data_table_id, 'selected_row_indices')])
def update_output(list_of_contents,
                  list_of_filenames,
                  rows,
                  selected_row_indices):
    
    output = []
    
    if not list_of_contents:
        
        return output
    
    if not selected_row_indices:
        
        return output
    
    #TODO:
    # Generate page for each experiment type 
    # Make the display of the results more vivid (distinctive colors)
    
    selected_experiments = map(lambda selected_row_index: rows[selected_row_index], selected_row_indices)
    
    selected_experiment_ids = tuple(map(lambda experiment: experiment['id'], selected_experiments))
    
    print(selected_experiment_ids)

    extracted_rows = script_sql_class.query.filter(script_sql_class.id.in_(selected_experiment_ids)).all()
    
    print(extracted_rows)
    # expunge all the models instances (done)
    map(db.session.expunge, extracted_rows)
    
    for contents, filename in zip(list_of_contents, list_of_filenames):
    
        if contents is not None:

            content_type, content_string = contents.split(',')

            if 'image' in content_type:
                
                output.append( html.H1(filename) )
                output.append(html.Img(src=contents))

                for row in extracted_rows:

                    img_np = convert_base64_image_string_to_numpy(content_string)

                    future_obj = task_manager.process_pool.schedule( script_sql_class.actions['inference'],
                                                                     args=(row, img_np) )

                    result_np = future_obj.result()

                    results_base64 = convert_numpy_to_base64_image_string(result_np)
                    
                    
                    output.append( html.H1( "Result of model id#{}".format(row.id) ) )
                    output.append( html.Img(src=results_base64) )

            
    return output