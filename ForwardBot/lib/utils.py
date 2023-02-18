"""
   Copyright 2023 VoxLight

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

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


