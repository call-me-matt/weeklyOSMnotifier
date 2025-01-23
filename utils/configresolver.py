import os
import collections
import yaml
from copy import deepcopy

from src import osmspam


class configResolver(object):
    def __init__(self, logger, args):
        self.logger = logger
        with open(os.path.join("configs", "configs.yaml"), "r") as hiryaml:
            self.hierarchy_conf = yaml.full_load(hiryaml)
            self.configs = collections.OrderedDict()
            self.args = args
            dummy_conf = osmspam.osmSPAM(logger)
            dummy_conf.load_params(args)
            dummy_conf.crawl_latest_weekly()
            dummy_conf.load_image()
            self.stack = list()
            self.stack.append(dummy_conf)
            self.load_hierarchy(self.hierarchy_conf)

    def load_hierarchy(self, processlist):
        for f in processlist:
            has_children = isinstance(f, dict)
            if has_children:
                fkey = list(f.keys())[0]
                fname = os.path.join("configs", fkey)
            else:
                fname = os.path.join("configs", f)

            if os.path.isfile(fname) == True:
                conf = deepcopy(self.stack[-1:][0])
                with open(fname, "r") as fstr:
                    data = yaml.full_load(fstr)
                    if data is not None:
                        conf.load_from_config(data)
                if conf.runnable == True:
                    self.configs[(conf.context, conf.lang)] = conf
                if has_children:
                    self.stack.append(conf)
                    self.load_hierarchy(f[fkey])
                    self.stack.pop()
            else:
                self.logger.error("File not found:" + fname)
