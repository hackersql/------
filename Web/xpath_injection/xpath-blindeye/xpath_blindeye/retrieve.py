import os
import hashlib
import logging
import traceback
from typing import Union
from xml.etree.ElementTree import Element, SubElement, parse, ElementTree

from xpath_blindeye.xnode import XNode
from xpath_blindeye.util import prettify
from xpath_blindeye.config import ROOT_PATH, URL

logger = logging.getLogger("xpath-blindeye")


def retrieve():
    url_md5 = hashlib.md5(URL.encode())
    try:
        os.mkdir('./saved_requests')
    except FileExistsError:
        pass
    save_location = './saved_requests/{}.xml'.format(url_md5.hexdigest())
    saved_root = None
    try:
        saved_tree = parse(save_location)
        saved_root = saved_tree.getroot()
    except FileNotFoundError:
        pass

    root_path = ROOT_PATH
    root_node_name = XNode.get_node_name(root_path)
    logger.info("Root node name is " + root_node_name)
    xml_root = Element(root_node_name)
    try:
        visit_node(root_node_name, root_path, None, xml_root, saved_root)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        traceback.print_exc()
    finally:
        print(prettify(xml_root))
        result = input("\n\nOverwrite last xml save?(Y/N)")
        if result.lower() != "y":
            exit(0)
        et = ElementTree(xml_root)
        logger.info("Saving...")
        et.write(save_location)


def visit_node(node_name: str, path: str, parent: Union[Element, None], xml_root: Element, saved_root: Element):
    if parent is None:
        node = xml_root
    else:
        node = SubElement(parent, node_name)  # type: Element
    xnode = XNode(node_name, path, parent, xml_root, saved_root)
    # Get and add attributes
    node.attrib = xnode.get_attributes()
    # Get and add text value
    node.text = xnode.get_node_text()
    # Get children
    child_names = xnode.get_child_node_names()
    # Do last
    for child_name, child_path in child_names:
        visit_node(node_name=child_name, path=child_path, parent=node, xml_root=xml_root, saved_root=saved_root)
