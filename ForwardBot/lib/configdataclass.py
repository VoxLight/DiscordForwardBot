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

from __future__ import annotations

import re
import configparser
from dataclasses import dataclass

from typing import Callable, Any, List

@dataclass
class ConfigDataClass:
    @classmethod
    def from_file(cls, path: str, *args, **kwargs) -> ConfigDataClass:
        config = configparser.ConfigParser(*args, **kwargs)
        config.read(path)
        return cls(config)

    @classmethod
    def empty(cls):
        return cls(configparser.ConfigParser())


    def __init__(
        self, 
        config: configparser.ConfigParser, 
        type_converters: List[Callable[[ConfigDataClass, str], (Any, bool)]] = [],
        do_type_conversion: bool = True,
    ):
        """Simply takes the dict-based ConfigParser class and converts it to a dataclass

        Args:
            config (configparser.ConfigParser):
                The configparser object which contains the configuration.
            type_converters (List[Callable[[\"Config\", str], Any]], optional): 
                List of type converters for strings. If none are provided, then
                will default to converting ints and lists. Defaults to [].
            do_type_conversion (bool, optional): 
                Whether or not to do the type conversions. Defaults to True.
        """        
        self.do_type_conversion = do_type_conversion
        if do_type_conversion:
            self.type_converters = (
                type_converters if type_converters 
                else [
                    self._convert_ints,
                    self._convert_lists
                ]
        )
        for section in config.sections():
            for key, value in config.items(section):
                if self.do_type_conversion:
                    setattr(self, key, self._try_convert_value(value))
                    continue
                setattr(self, key, value)
                

    def _try_convert_value(self, value: str) -> Any:
        for converter in self.type_converters:
                val, success = converter(self, value)
                if success:
                    return val
        return value

    @staticmethod
    def _convert_ints(config: ConfigDataClass, value: str) -> (int, bool):
        if (value.isdigit()): return int(value), True
        return value, False

    @staticmethod
    def _convert_lists(config: ConfigDataClass, value) -> (List[Any], bool):        
        if value[0]=="[" and value[-1]=="]":
            return [
                config._try_convert_value(v) for v in re.findall(r'\d+', value)
            ], True
        return value, False
