from . import configdataclass, defaultbot
import os

def make_path(path):

    directory = os.path.dirname(path)

    if not os.path.exists(directory):
        print(directory)
        os.makedirs(directory)

def get_config():
    # make sure we have a config file
    # and if not, create one
    config = None
    try:
        return configdataclass.ConfigDataClass.from_file(defaultbot.DefaultBot.CONFIG_LOCATION)
    except FileNotFoundError:
        return _make_config()
        
def _make_config(self):
    # TODO: This later...
    return configdataclass.ConfigDataClass.empty()


