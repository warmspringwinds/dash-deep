from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go


class BaseSegmentationGraph():
    
    def __init__(self, height=600, width=600):
        
        figure_obj = tools.make_subplots(rows=2, cols=1,
                                         subplot_titles=('Losses', 'Accuracy'))
        
        trace1 = go.Scatter(
                            x=[],
                            y=[]
                            )

        trace2 = go.Scatter(
                            x=[],
                            y=[]
                        )
        
        figure_obj.append_trace(trace1, 1, 1)
        figure_obj.append_trace(trace2, 2, 1)

        figure_obj['layout'].update(height=height,
                                    width=width)
        
        self.figure_obj = figure_obj.get_ordered()
        