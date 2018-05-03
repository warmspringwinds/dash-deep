import click

from dash_deep.utils import generate_wtform_instances_and_input_form_widjets
from dash_deep.scripts.semantic_segmentation_train_script import PascalSegmentation
from dash_deep.cli.interface_factory import generate_click_cli


forms, widjets = generate_wtform_instances_and_input_form_widjets([PascalSegmentation])


def function_to_be_wrapped(**kwargs):
    
    print(kwargs)

    
form = forms[0]
widjets = widjets[0]

cli = generate_click_cli(form, function_to_be_wrapped)


if __name__ == '__main__':
    cli()
    