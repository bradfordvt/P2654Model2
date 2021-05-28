#!/usr/bin/env python
"""
    NodeContainer is a helper class used to cache association information used to look up nodes instances.
    Copyright (C) 2021  Bradford G. Van Treuren

    NodeContainer is a helper class used to cache association information used to look up nodes instances.
    The application uses the NodeContainer to locate a node instance based on either the dot path name
    or the UUID.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

__authors__ = ["Bradford G. Van Treuren"]
__contact__ = "bradvt59@gmail.com"
__copyright__ = "Copyright 2021, VT Enterprises Consulting Services"
__credits__ = ["Bradford G. Van Treuren"]
__date__ = "2021/02/25"
__deprecated__ = False
__email__ = "bradvt59@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Bradford G. Van Treuren"
__status__ = "Alpha/Experimental"
__version__ = "0.0.1"


import logging
from autologging import traced, logged


module_logger = logging.getLogger('p2654model2.builder.nodecontainer')


@logged
@traced
class NodeContainer(object):
    inst = None

    @staticmethod
    def get_nodecontainer():
        if NodeContainer.inst is None:
            NodeContainer.inst = NodeContainer()
        return NodeContainer.inst

    def __init__(self):
        self.container = []
        self.key_obj_map = {}
        self.path_key_map = {}
        self.key_path_map = {}
        self.top = None

    def add_node(self, node):
        self.key_obj_map[len(self.container)] = node
        self.container.append(node)

    def define_top(self, top_node):
        self.top = top_node

    def get_next_node_id(self):
        return len(self.container)

    def get_node_by_id(self, _id):
        if _id < 0 or _id > len(self.container) - 1:
            raise ValueError("Identifier ({:d}) is out of range!".format(_id))
        return self.container[_id]

    def get_node_by_path(self, _path):
        key = self.path_key_map.get(_path)
        node = self.key_obj_map.get(key)
        if node is None and len(self.path_key_map.keys()) == 0:
            # Build cache to speed up access for later calls
            self.__build_path_cache()
            key = self.path_key_map.get(_path)
            node = self.key_obj_map.get(key)
        if node is None:
            raise ValueError("Path ({:s}) does not exist".format(_path))
        return node

    def get_path_by_id(self, _id):
        path = self.key_path_map.get(_id)
        if path is None and len(self.key_path_map.keys()) == 0:
            # Build cache to speed up access for later calls
            self.__build_path_cache()
            path = self.key_path_map.get(_id)
        if path is None:
            raise ValueError("ID ({:d}) does not exist".format(_id))
        return path

    def __build_path_cache(self):
        if self.top is None:
            raise AssertionError("top has not been defined.")
        # Depth first search to discover path to node
        parent = self.top.name
        self.key_obj_map[0] = self.top
        self.path_key_map[parent] = 0
        self.key_path_map[0] = parent
        child = self.top
        children = child.get_children()
        for c in children:
            if c.visible:
                for k in self.key_obj_map.keys():
                    if c == self.key_obj_map[k]:
                        self.path_key_map[parent + "." + c.name] = k
                        self.key_path_map[k] = parent + "." + c.name
                        self.__build_subpath_cache(parent + "." + c.name, c)
            else:
                self.__build_subpath_cache(parent, c)

    def __build_subpath_cache(self, parent, node):
        children = node.get_children()
        for c in children:
            if c.visible:
                for k in self.key_obj_map.keys():
                    if c == self.key_obj_map[k]:
                        self.path_key_map[parent + "." + c.name] = k
                        self.key_path_map[k] = parent + "." + c.name
                        self.__build_subpath_cache(parent + "." + c.name, c)
            else:
                self.__build_subpath_cache(parent, c)

    def dump(self):
        print("Dumping path cache:")
        self.__build_path_cache()
        print(str(self.container))
        for key in self.path_key_map.keys():
            print("path = {:s}, uid = {:d}".format(key, self.key_obj_map[self.path_key_map[key]].uid))
