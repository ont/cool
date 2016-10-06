import yaml

class Config:
    """Class for parsing YAML file and representing its internal structure.."""

    def __init__(self, fname):
        """Parse YAML file

        :fname: filename of YAML config

        """
        self.yaml = yaml.load(open(fname))

        self.storage = self.yaml['options']['storage']
        self.queue = self.yaml['options']['queue']
        self.boxes = self.yaml['boxes']

