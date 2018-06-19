from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
from copy import deepcopy


def convert_column_name_to_legend_name(column_name):
    """Converts a column variable name in underscore notation into a plot's
    legend name.
    
    Replaces underscores with spaces and capitalizes the input variable
    name. For example, 'validation_score' -> 'Validation score'.
    
    Parameters
    ----------
    column_name : string
        String representing the variable name.
    
    Returns
    -------
    legend_name : string
        String representing the legend name.
    """
    
    return column_name.replace('_', ' ').capitalize()


def flatten_list(two_dimensional_list):
    """Flattens 2D nested list.
    
    See more here:
    https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
    
    This operation is necessary because plotly's API accepts titles
    for a created graph with subplots as a flattened list of positions of subplots.
    
    Parameters
    ----------
    two_dimensional_list : list of lists
        List of lists.
    
    Returns
    -------
    flattened : list
        Flattened list.
    """
    
    flattened = [item for sublist in two_dimensional_list for item in sublist]
    
    return flattened


class BaseGraph():
    """Class that takes care of storing of Plotly's dict representation
    of a graph with subplots.
    
    The class accepts the graph definition with subplots titles and 
    traces legend names that each subplot contains. We store the dict
    representation because original plotly's representation of a graph
    is not serializable and therefore we can't store it in a pickle format.
    
    """
    
    def __init__(self, graph_definition):
        """Accepts the graph definition dict, creates plotly's graph object
        from it and converts it into a dict representation which is being stored
        internally. Instances of this classes are serializable and can be stored
        in a pickle column type in sqlalchemy.
        
        About the graph definition rules:
        
        It's a 2D nested list where each element represents subplot.
        
        For example:
        
        graph_definition = [ 
                               [ ('Losses', ['training_loss', 'validation_loss']),
                                 ('Accuracy', ['training_accuracy', 'validation_accuracy']) ]
                           ]
                           
        Defines a graph with with one row and two columns of subplots.
        
        Each subplot is represented by tuple where the first element is desired title of the
        subplot. Second element is a list of legend names for traces that will be displaed
        in this subplot. In our example, ('Losses', ['training_loss', 'validation_loss']) will
        have a title of 'Losses' and two traces 'training_loss' and 'validation_loss'.
        The class has a method add_next_iteration_results() which accepts named arguments that
        will append new values to the repective traces.
        
        

        Parameters
        ----------
        graph_definition : list
            List with the graph definition

        """
        
        self.subplot_trace_iteration_counters = {}
        
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
            
            self.subplot_trace_iteration_counters[graph_name] = 0
            self.graph_column_name_trace_mapping[graph_name] = trace
            
    
    
    def add_next_iteration_results(self, **kwargs):
        """Appends next values to traces of the graph object.
    
        The function accepts the named arguments -- where
        names are the same as provided in the graph definition for
        traces.
        
        For this example:
        
        graph_definition = [ 
                               [ ('Losses', ['training_loss', 'validation_loss']),
                                 ('Accuracy', ['training_accuracy', 'validation_accuracy']) ]
                           ]
        Named arguments will be 'training_loss', 'validation_loss',
        'training_accuracy', 'validation_accuracy'.

        Parameters
        ----------
        kwargs : Named arguments
            Named arguments representing traces to append
            with new values.

        """
                
        # Appending the next step values
        for trace_name, trace_value_to_append in kwargs.iteritems():
            
            current_trace_iteration_counter = self.subplot_trace_iteration_counters[trace_name]
            self.graph_column_name_trace_mapping[trace_name]['x'].append(current_trace_iteration_counter)
            self.subplot_trace_iteration_counters[trace_name] += 1
            
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