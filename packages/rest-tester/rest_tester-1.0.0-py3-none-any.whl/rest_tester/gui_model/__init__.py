"""
GUI Model layer for REST Tester application.
Contains data models and GUI widgets for server and client instances.
"""

from .model import ConfigModel, ServerInstance, ClientInstance
from .base_instance_widget import BaseInstanceWidget
from .server_instance_gui import ServerInstanceWidget
from .client_instance_gui import ClientInstanceWidget
from .defaults_widget import DefaultsWidget
from .instances_gui import MainWindow

__all__ = [
    'ConfigModel', 
    'ServerInstance', 
    'ClientInstance',
    'BaseInstanceWidget',
    'ServerInstanceWidget',
    'ClientInstanceWidget',
    'DefaultsWidget',
    'MainWindow'
]
