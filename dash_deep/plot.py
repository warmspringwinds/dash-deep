from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
from copy import deepcopy


# class BaseGraph():
    
#     def __init__(self):
        
#         self.iteration_counter = 0
        
#         # Creating two subplots with two columns
#         figure_obj = tools.make_subplots(rows=1, cols=2,
#                                          subplot_titles=('Losses', 'Accuracy'))
        
#         # Creating curves for val/train accuracy/loss curves
#         training_loss_curve_trace = go.Scatter(
#                                             x=[],
#                                             y=[],
#                                             name = 'Training loss')

#         validation_loss_curve_trace = go.Scatter(
#                                             x=[],
#                                             y=[],
#                                             name = 'Validation loss')

#         training_accuracy_curve_trace = go.Scatter(
#                                             x=[],
#                                             y=[],
#                                             name = 'Training accuracy')


#         validation_accuracy_curve_trace = go.Scatter(
#                                             x=[],
#                                             y=[],
#                                             name = 'Validation accuracy')

#         # associating our scatter objects with each subplot
#         figure_obj.append_trace(training_loss_curve_trace, 1, 1)
#         figure_obj.append_trace(validation_loss_curve_trace, 1, 1)
#         figure_obj.append_trace(training_accuracy_curve_trace, 1, 2)
#         figure_obj.append_trace(validation_accuracy_curve_trace, 1, 2)

#         #figure_obj['layout'].update(height=height,
#         #                            width=width)
        
#         # Plotly's Figure objects are not serializable,
#         # therefore we convert them into ordered dict and serilize
#         # later to store in the pickle format inside of our db.
#         self.figure_obj = figure_obj.get_ordered()
        
#         # Creating sym links for all curves,
#         # so that we can easily update the object
#         self.training_loss_history = self.figure_obj['data'][0]
#         self.validation_loss_history = self.figure_obj['data'][1]
#         self.training_accuracy_history = self.figure_obj['data'][2]
#         self.validation_accuracy_history = self.figure_obj['data'][3]
    
    
#     def add_next_iteration_results(self,
#                                    training_loss,
#                                    validation_loss,
#                                    training_accuracy,
#                                    validation_accuracy):
        
        
#         self.training_loss_history['x'].append(self.iteration_counter)
#         self.validation_loss_history['x'].append(self.iteration_counter)
#         self.training_accuracy_history['x'].append(self.iteration_counter)
#         self.validation_accuracy_history['x'].append(self.iteration_counter)
#         self.iteration_counter += 1
        
#         self.training_loss_history['y'].append(training_loss)
#         self.validation_loss_history['y'].append(validation_loss)
#         self.training_accuracy_history['y'].append(training_accuracy)
#         self.validation_accuracy_history['y'].append(validation_accuracy)



def convert_column_name_to_legend_name(column_name):
    
    return column_name.replace('_', ' ').capitalize()


def flatten_list(two_dimensional_list):
    
    flattened = [item for sublist in two_dimensional_list for item in sublist]
    
    return flattened

class BaseGraph():
    
    def __init__(self, graph_definition):
        
        self.iteration_counter = 0
        
        # Inferring the number the size of
        # our figure with subplots
        rows = len(graph_definition)
        cols = len(graph_definition[0])
        
        self.rows = rows
        self.cols = cols
        
        self.graph_column_names = []
        self.graph_column_name_trace_mapping = {}
        
        # Flattening our 2D array representing subplots
        # in order to correctly provide subplots' titles
        graph_definition_flattened = flatten_list(graph_definition)
        self.subplot_titles = [graph[0] for graph in graph_definition_flattened]

        # Actually creating the plot with subplots
        figure_obj = tools.make_subplots(rows=rows, cols=cols,
                                         subplot_titles=self.subplot_titles)

        for current_row in xrange(rows):

            for current_col in xrange(cols):
                
                # Each subplot can have a list of traces -- for example
                # Loss subplot usually contains validation and train loss
                current_subplot_traces_names = graph_definition[current_row][current_col][1]
                
                # Creating trace instances
                for sublot_trace_name in current_subplot_traces_names:
                    
                    # Converting the column name into actual title
                    # like from validation_loss to Validation loss
                    legend_name = convert_column_name_to_legend_name(sublot_trace_name)

                    current_trace = go.Scatter(
                                            x=[],
                                            y=[],
                                            name=legend_name)
                    
                    # +1 because in plot.ly's subplots are numerated starting from 1 and not 0
                    figure_obj.append_trace(current_trace, current_row + 1, current_col + 1)
                    
                    self.graph_column_names.append(sublot_trace_name)
        
        # Plotly's Figure objects are not serializable,
        # therefore we convert them into ordered dict and serilize
        # later to store in the pickle format inside of our db.
        self.figure_obj = figure_obj.get_ordered()
        
        # Creating a mapping from trace name to its location in the dict representation
        # of plot.ly's Figure object
        for graph_name, trace in zip(self.graph_column_names, self.figure_obj['data']):

            self.graph_column_name_trace_mapping[graph_name] = trace
    
    
    def add_next_iteration_results(self, **kwargs):
        
        # Updating the counter for each trace
        for current_trace in self.graph_column_name_trace_mapping.values():
            
            current_trace['x'].append(self.iteration_counter)
        
        self.iteration_counter += 1
        
        # Appending the next step values
        for trace_name, trace_value_to_append in kwargs.iteritems():
            
            self.graph_column_name_trace_mapping[trace_name]['y'].append(trace_value_to_append)

        
        
def create_model_plot_with_unique_legends(sql_model_instance):
    """Extracts the plot object form sql model instance and adds unique
    id onto its legends.
    
    Extracts the figure object that can be passed to dash.Graph object
    and displayed. Adds a unique ID (which is acquired from sql model instance
    database ID) to its legends. This is useful when the figure needs to be
    combined with figures of other sql model instances, otherwise it is impossible
    to differentiate between objects in the figure.
    
    Parameters
    ----------
    sql_model_instance : instance of sqlalchemy model
        Instance of sqlalchemy model.
    
    Returns
    -------
    model_plot : dict
        Dict representing the plotly's figure.
        Can be passed to dash's graph object.
    """
    
    model_plot = deepcopy(sql_model_instance.graphs.figure_obj)
    
    for trace in model_plot['data']:
    
        trace['name'] = trace['name'] + " (Experiment ID: {})".format(sql_model_instance.id)
                          
    return model_plot

                          
def create_mutual_plot(sql_model_instances):
    """Creates a mutual figure for multiple sql model instances of the same type.
    
    Extracts figures from each sql models instance and adds ID number of
    the model to legends of each figure. This way curves of of different
    sql model instances can be differentiated.
    
    Parameters
    ----------
    sql_model_instances : list
        List of instances of sqlalchemy model
    
    Returns
    -------
    mutual_figure : dict
        Dict representing the plotly's figure.
        Can be passed to dash's graph object.
    """
    
    mutual_figure = {'data':[], 'layout': []}
    
    if sql_model_instances:
        
        mutual_figure = create_model_plot_with_unique_legends(sql_model_instances[0])
    
    for sql_model_instance in sql_model_instances[1:]:
        
        current_model_plot_with_unique_legends = create_model_plot_with_unique_legends(sql_model_instance)
        
        mutual_figure['data'] = mutual_figure['data'] + current_model_plot_with_unique_legends['data']
    
    return mutual_figure