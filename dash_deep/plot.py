from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go


class BaseSegmentationGraph():
    
    
    def __init__(self, height=600, width=1000):
        
        # Creating two subplots with two columns
        figure_obj = tools.make_subplots(rows=1, cols=2,
                                         subplot_titles=('Losses', 'Accuracy'))
        
        # Creating curves for val/train accuracy/loss curves
        training_loss_curve_trace = go.Scatter(
                                            x=[],
                                            y=[],
                                            name = 'Training loss')

        validation_loss_curve_trace = go.Scatter(
                                            x=[],
                                            y=[],
                                            name = 'Validation loss')

        training_accuracy_curve_trace = go.Scatter(
                                            x=[],
                                            y=[],
                                            name = 'Training accuracy')


        validation_accuracy_curve_trace = go.Scatter(
                                            x=[],
                                            y=[],
                                            name = 'Validation accuracy')

        # associating our scatter objects with each subplot
        figure_obj.append_trace(training_loss_curve_trace, 1, 1)
        figure_obj.append_trace(validation_loss_curve_trace, 1, 1)
        figure_obj.append_trace(training_accuracy_curve_trace, 1, 2)
        figure_obj.append_trace(validation_accuracy_curve_trace, 1, 2)

        #figure_obj['layout'].update(height=height,
        #                            width=width)
        
        # Plotly's Figure objects are not serializable,
        # therefore we convert them into ordered dict and serilize
        # later to store in the pickle format inside of our db.
        self.figure_obj = figure_obj.get_ordered()
        
        # Creating sym links for all curves,
        # so that we can easily update the object
        self.training_loss_history = self.figure_obj['data'][0]
        self.validation_loss_history = self.figure_obj['data'][1]
        self.training_accuracy_history = self.figure_obj['data'][2]
        self.validation_accuracy_history = self.figure_obj['data'][3]
        