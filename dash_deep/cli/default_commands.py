import click
from dash_deep.app import server, db


@server.cli.command()
@click.argument('host', default='0.0.0.0')
@click.argument('port', default='5000')
def run_server(port, host):
    """Starts a web server for running ML scripts.
    
    Starts a web server which provides an interactive intefrace
    for running and managing ML experiments defined in a 
    dash_deep/models.py file.
    """
    
    server.run(port=port, host=host)
    
@server.cli.command()
def drop_database():
    """Drops all tables related to experiments results.
    
    Deletes all the records and tables that were created based
    on experiments defined in dash_deep/models.py. Use carefully,
    you might loose all your experiments data.
    """
    
    db.drop_all()
    
@server.cli.command()
def initiate_database():
    """Initiates all tables related to experiments.
    
    Creates all tables that are defined in dash_deep/models.py
    file. These tables will be populated while running experiments
    through we interface or command line interface.
    """
    
    db.create_all()


    