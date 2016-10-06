import importlib

from server.box import Box
from common.path import DatePath

class Loader(object):
    """Class for loading boxes/indexes from config"""

    def __init__(self, config):
        """
        :config: instance of Config class for loading from (parsed yaml).

        """
        self.config = config


    def load_boxes(self):
        """Loads all boxes from config file.

        :returns: list of Box's.

        """
        return [ self.load_box(name) for name in self.config.boxes ]


    def load_box(self, name):
        """Loads particular box from config or returns basic box if there is no
        config for such name.

        :name: name of the box to load
        :returns: Box

        """

        config = self.config.boxes.get(name, None)
        if config:
            indexes = self.load_indexes( config, name )
            return Box(name, self.config.storage, indexes)

        return Box(name, self.config.storage)  ## return box without indexes


    def load_indexes(self, box_config, box_name):
        """load indexes from YAML subtree

        :box_config: YAML subtree with config for box
        :box_name: name of the box for which indexes is loaded
        :returns: loaded indexes

        """
        if not box_config['indexes']:
            return []

        res = []
        for iconf in box_config['indexes']:
            pmod = importlib.import_module('server.parsers.' + iconf['parser'])
            imod = importlib.import_module('server.indexes.' + iconf['type'])

            index = imod.Index(
                DatePath(self.config.storage).join(box_name),
                pmod.Parser()
            )
            res.append(index)
            print('parser ->', iconf['parser'], pmod)
            print('index ->', iconf['type'], imod)

        return res
