from abc import ABC, abstractmethod
import xmltodict
from harvestmouseapp.mvc_model.model import Mouse, MouseList, Record, AdvancedRecord


class MouseModelAdapter(ABC):

    @abstractmethod
    def transform(self, raw_date):
        pass


def parse_sub_record(raw_dict):
    try:
        record = Record(
            liver=raw_dict['liver'],
            liver_tumor=raw_dict['liver_tumor'],
            others=raw_dict['others']
        )
        return record
    except KeyError as e:
        return e


def parse_sub_advanced_record(raw_dict):
    try:
        record = AdvancedRecord(
            liver=raw_dict['liver'],
            liver_tumor=raw_dict['liver_tumor'],
            small_intenstine=raw_dict['small_intenstine'],
            small_intenstine_tumor=raw_dict['small_intenstine_tumor'],
            skin=raw_dict['skin'],
            skin_tumor=raw_dict['skin_tumor'],
            others=raw_dict['others']
        )
        return record
    except KeyError as e:
        return e


def parse_mouse(raw_dict):
    try:
        mouse = Mouse(
            physical_id=raw_dict['physical_id'],
            handler=raw_dict['handler'],
            gender=raw_dict['gender'],
            mouseline=raw_dict['mouseline'],
            genotype=raw_dict['genotype'],
            birth_date=raw_dict['birth_date'],
            end_date=raw_dict['end_date'],
            cog=raw_dict['cog'],
            phenotype=raw_dict['phenotype'],
            project_title=raw_dict['project_title'],
            comment=raw_dict['comment']
        )
        if 'pfa_record' in raw_dict.keys():
            pfa_record_xml = raw_dict['pfa_record']
            mouse.pfa_record = parse_sub_advanced_record(pfa_record_xml)
        if 'freeze_record' in raw_dict.keys():
            freeze_record_xml = raw_dict['freeze_record']
            mouse.freeze_record = parse_sub_record(freeze_record_xml)

        return mouse
    except KeyError as e:
        return e


class XmlModelAdapter(MouseModelAdapter):
    """
    Example of mouse xml raw data
    <mouse>
       <physical_id></physical_id>
       <handler></handler>
       <gender></gender>
       <mouseline></mouseline>
       <genotype></genotype>
       <birth_date></birth_date>
       <end_date></end_date>
       <cog></cog>
       <phenotype></phenotype>
       <project_title></project_title>
    </mouse>

    Example of mouse list raw data
    <mouselist>
    <mouse>
       <physical_id></physical_id>
       <handler></handler>
       <gender></gender>
       <mouseline></mouseline>
       <genotype></genotype>
       <birth_date></birth_date>
       <end_date></end_date>
       <cog></cog>
       <phenotype></phenotype>
       <project_title></project_title>
    </mouse>
    ...
    </mouselist>
    """

    def transform(self, raw_data):
        # read the raw value of the xml data
        xml_parsed = xmltodict.parse(raw_data)
        moust_list = MouseList()
        # Check if it's a list of mouse in the raw_data

        if 'mouselist' in xml_parsed.keys():
            # start parsing each of the mouse
            if 'mouse' in xml_parsed['mouselist'].keys():
                # list_xml can be a list or a single mouse xml
                list_xml = xml_parsed['mouselist']['mouse']

                if not isinstance(list_xml, list):
                    # return the successful parse mouse
                    return parse_mouse(list_xml)
                else:
                    # 2 or more mouse found
                    for m in list_xml:
                        moust_list.add_mouse(parse_mouse(m))
                    return moust_list
        else:
            if 'mouse' in xml_parsed.keys():
                # list_xml can be a list or a single mouse xml
                single_mouse_xml = xml_parsed['mouse']
                return parse_mouse(single_mouse_xml)

        # Fall through to here means none of the mouse or mouselist
        # appear in the xml file
        return None


