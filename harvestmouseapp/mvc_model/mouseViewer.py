from abc import ABC, abstractmethod
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
from harvestmouseapp.mvc_model.model import Mouse, MouseList


class Viewer:

    def __init__(self):
        self._viewer = None

    def _set_viewer(self, viewer):
        self._viewer = viewer

    def transform(self, mouse_data):
        return self._viewer.transform(mouse_data)


class GenericMouseViewer(ABC):
    @abstractmethod
    def transform(self, mouse_data):
        pass


def _create_sub_node_from(node, tag_name, value=None):
    sub_node = SubElement(node, tag_name)
    if value is not None:
        sub_node.text = str(value)
    return sub_node


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


class XmlMouseViewer(GenericMouseViewer):
    def __init__(self):
        self.document = None
        self.cur_mouse_node = None

    def transform(self, mouse_data):
        root_node = None
        if isinstance(mouse_data, MouseList):
            root_node = self._create_root_node('mouselist')

        if isinstance(mouse_data, MouseList):
            next_node = None
            # initialize to comment node first
            for m in mouse_data:
                # append node will override parent node option
                next_node = self._add_mouse_node(mouse=m, parent_node=root_node)
        else:
            # append node will override parent node option
            mouse_node = self._add_mouse_node(mouse=mouse_data)

        return prettify(self.document)

    def _create_root_node(self, root_node_name):
        self.document = Element(root_node_name)
        return self.document

    def _create_comment_node(self, comment):
        comment = Comment(comment)
        if self.document is not None:
            self.document.append(comment)
        else:
            self.document = comment

        return comment

    def _add_mouse_node(self, mouse, parent_node=None):
        # if parent_node is absent
        # either we append to the document or
        # we make this a the root node to the document
        if parent_node is None:
            mouse_node = Element('mouse')
            if self.document:
                self.document.append(mouse_node)
            else:
                self.document = mouse_node
        else:
            mouse_node = SubElement(parent_node, 'mouse')

        _create_sub_node_from(mouse_node, 'physical_id', mouse.physical_id)
        _create_sub_node_from(mouse_node, 'handler', mouse.handler)
        _create_sub_node_from(mouse_node, 'gender', mouse.gender)
        _create_sub_node_from(mouse_node, 'mouseline', mouse.mouseline)
        _create_sub_node_from(mouse_node, 'genotype', mouse.genotype)
        _create_sub_node_from(mouse_node, 'birth_date', mouse.birth_date)
        _create_sub_node_from(mouse_node, 'end_date', mouse.end_date)
        _create_sub_node_from(mouse_node, 'cog', str(mouse.cog))
        _create_sub_node_from(mouse_node, 'phenotype', mouse.phenotype)
        _create_sub_node_from(mouse_node, 'project_title', mouse.project_title)
        _create_sub_node_from(mouse_node, 'comment', mouse.comment)

        pfa_node = SubElement(mouse_node, 'pfa_record')
        freeze_node = SubElement(mouse_node, 'freeze_record')

        _create_sub_node_from(pfa_node, 'liver', value=mouse.pfa_record.liver)
        _create_sub_node_from(pfa_node, 'liver_tumor', value=mouse.pfa_record.liver_tumor)
        _create_sub_node_from(pfa_node, 'small_intenstine', value=mouse.pfa_record.small_intenstine)
        _create_sub_node_from(pfa_node, 'small_intenstine_tumor', value=mouse.pfa_record.small_intenstine_tumor)
        _create_sub_node_from(pfa_node, 'skin', value=mouse.pfa_record.skin)
        _create_sub_node_from(pfa_node, 'skin_tumor', value=mouse.pfa_record.skin_tumor)
        _create_sub_node_from(pfa_node, 'others', value=mouse.pfa_record.others)

        _create_sub_node_from(freeze_node, 'liver', value=mouse.freeze_record.liver)
        _create_sub_node_from(freeze_node, 'liver_tumor', value=mouse.freeze_record.liver_tumor)
        _create_sub_node_from(freeze_node, 'others', value=mouse.freeze_record.others)

        return mouse_node




