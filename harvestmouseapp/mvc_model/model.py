"""
This module contains variery of model class
to support the MVC model
"""
import datetime
from enum import Enum


class ColumnList(Enum):
    header_name = '_Mouse__'
    PHYSICAL_ID_COL = header_name + 'physical_id'
    HANDLER_COL = header_name + 'handler'
    GENDER_COL = header_name + 'gender'
    MOUSE_LINE_COL = header_name + 'mouseline'
    GENOTYPE_COL = header_name + 'genotype'
    BIRTH_DATE = header_name + 'birth_date'
    END_DATE = header_name + 'end_date'
    COG_DATE = header_name + 'cog'
    PHENOTYPE = header_name + 'phenotype'
    PROJECT_TITLE_COL = header_name + 'project_title'
    EXPERIMENT_COL = header_name + 'experiment'
    COMMENT_COL = header_name + 'comment'


def replace_mouse_with_new_data(new_mouse_input, old_mouse_input):
    old_mouse_input.handler = new_mouse_input.handler
    old_mouse_input.gender = new_mouse_input.gender
    old_mouse_input.mouseline = new_mouse_input.mouseline
    old_mouse_input.genotype = new_mouse_input.genotype
    old_mouse_input.birth_date = new_mouse_input.birth_date
    old_mouse_input.end_date = new_mouse_input.end_date
    old_mouse_input.cog = new_mouse_input.cog
    old_mouse_input.phenotype = new_mouse_input.phenotype
    old_mouse_input.project_title = new_mouse_input.project_title
    old_mouse_input.experiment = new_mouse_input.experiment
    old_mouse_input.comment = new_mouse_input.comment
    replace_record_with_new_data(new_mouse_input.freeze_record, old_mouse_input.freeze_record)
    replace_advanced_record_with_new_data(new_mouse_input.pfa_record, old_mouse_input.pfa_record)


def replace_record_with_new_data(new_record_input, old_record_input):
    old_record_input.liver = new_record_input.liver
    old_record_input.liver_tumor = new_record_input.liver_tumor
    old_record_input.others = new_record_input.others


def replace_advanced_record_with_new_data(new_record_input, old_record_input):
    replace_record_with_new_data(new_record_input, old_record_input)
    old_record_input.small_intenstine = new_record_input.small_intenstine
    old_record_input.small_intenstine_tumor = new_record_input.small_intenstine_tumor
    old_record_input.skin = new_record_input.skin
    old_record_input.skin_tumor = new_record_input.skin_tumor


class MouseList:
    """
    Mouse List class, contains the basic logic to handle the list of mouse
    """

    def __init__(self):
        self._mouse_list = []  # newly created array to store the mouse

    def add_mouse(self, mouse_input):
        # In here, we use simple if checking for the function
        # overloading of add mouse

        # check if the given input bounds with Mouse type
        if not check_if_mouse_type(mouse_input):
            return False

        # Replace with new mouse if found already in the list
        if self.is_mouse_in_list(mouse_input=mouse_input, list_check_by_id=True):
            self.remove_mouse(mouse_input)

        if is_list(mouse_input):
            self._mouse_list.extend(mouse_input)
        else:
            self._mouse_list.append(mouse_input)

        return True

    def remove_mouse(self, mouse_input):
        # check if the given input bounds with Mouse type
        if not check_if_mouse_type(mouse_input):
            return False

        # Getting the actual reference of the mouse
        # in the list
        # regarding to the list, if any of the mouse
        # not found in the list, return False to the
        # caller
        actual_ref = None
        if is_list(mouse_input):
            actual_ref = []
            for m in mouse_input:
                if self.is_mouse_in_list(physical_id=m.physical_id):
                    actual_ref.append(self.get_mouse_by_id(physical_id=m.physical_id))
                else:
                    return False  # one of the mouse not found in the current list
        else:
            # Use the physical id to find the mouse from the list
            actual_ref = self.get_mouse_by_id(physical_id=mouse_input.physical_id)

            # if actual_ref is None, means not exists in the list
            if actual_ref is None:
                return False  # return false to indicate the mouse not in the list

        if is_list(actual_ref):
            for m in actual_ref:
                self._mouse_list.remove(m)
        else:
            self._mouse_list.remove(actual_ref)

        return True

    def update_mouse(self, mouse_input):
        if not check_if_mouse_type(mouse_input):
            return False

        if is_list(mouse_input):
            for m in mouse_input:
                actual_ref = self.get_mouse_by_id(physical_id=m.physical_id)
                replace_mouse_with_new_data(m, actual_ref)
        else:
            actual_ref = self.get_mouse_by_id(physical_id=mouse_input.physical_id)
            replace_mouse_with_new_data(mouse_input, actual_ref)

    def get_size(self):
        #  get the size of the current moust list
        return len(self._mouse_list)

    def clear(self):
        #  Reset the mouse list to empty
        self._mouse_list = []

    def is_mouse_in_list(self, mouse_input=None, physical_id=None, list_check_by_id=False):
        # if mouse_input is given, checkeds all the mouse attributes
        # if physical_id is given, checks only physical_id
        # id should be independent, no duplication

        if mouse_input is not None:
            # check if the given input bounds with Mouse type
            if not check_if_mouse_type(mouse_input):
                return False

            found = False

            if is_list(mouse_input):
                for m in self._mouse_list:
                    for m_o in mouse_input:
                        if not list_check_by_id:
                            if m == m_o:
                                found = True
                                break
                        else:
                            if m.physical_id == m_o.physical_id:
                                found = True
                                break
                        found = False
                    if not found:
                        return False

            else:
                for m in self._mouse_list:
                    if not list_check_by_id:
                        if m == mouse_input:
                            found = True
                            break
                    else:
                        if m.physical_id == mouse_input.physical_id:
                            found = True
                            break
                    found = False
        else:
            found = False
            for m in self._mouse_list:
                if m.physical_id == physical_id:
                    found = True
                    break
                found = False
        return found

    def get_mouse_by_id(self, physical_id):
        if self.is_mouse_in_list(physical_id=physical_id):
            for m in self._mouse_list:
                if m.physical_id == physical_id:
                    return m
        return None

    """
    Override list built-in function to support
    native array manipulation
    """

    def __iter__(self):
        # Reset the index number to 0 for iterator
        return iter(self._mouse_list)

    def __len__(self):
        return self.get_size()

    def __getitem__(self, key):
        return self._mouse_list[key]

    # Equal if all the mouse attributes are exactly the same
    def __eq__(self, other):
        if not (self.get_size() == other.get_size()):
            return False

        for m in self._mouse_list:
            if not (other.is_mouse_in_list(mouse_input=m)):
                return False

        return True


class Mouse:
    """
    Mouse class, contains the basic information of the harvested mouse
    """

    def __init__(self, physical_id, handler, gender, mouseline, genotype,
                 birth_date, end_date, cog, phenotype, project_title, experiment, comment):
        self.physical_id = physical_id  # Physical ID of the mouse
        self.handler = handler  # Handler of the harvested mouse
        self.gender = gender  # Gender of the mouse
        self.mouseline = mouseline  # mouseline of the mouse
        self.genotype = genotype  # genotype of the mouse
        self.birth_date = birth_date  # birth date of the mouse
        self.end_date = end_date  # ended date of the mouse
        self.cog = cog  # Confirmation of genotype of the mouse
        self.phenotype = phenotype  # Phenotype of the mouse
        self.project_title = project_title  # project tile of the mouse
        self.experiment = experiment
        self.comment = comment
        self.pfa_record = AdvancedRecord()  # Instantiate a new Record
        self.freeze_record = Record()  # Instantiate a new AdvancedRecord

    def __str__(self):
        return self.physical_id

    def __eq__(self, other):
        return self.physical_id == other.physical_id and \
               self.handler == other.handler and \
               self.gender == other.gender and \
               self.mouseline == other.mouseline and \
               self.genotype == other.genotype and \
               self.birth_date == other.birth_date and \
               self.end_date == other.end_date and \
               self.cog == other.cog and \
               self.phenotype == other.phenotype and \
               self.project_title == other.project_title and \
               self.experiment == other.experiment and \
               self.comment == other.comment and \
               self.pfa_record == other.pfa_record and \
               self.freeze_record == other.freeze_record

    @property
    def physical_id(self):
        return self.__physical_id

    @physical_id.setter
    def physical_id(self, physical_id):
        self.__physical_id = physical_id

    @property
    def handler(self):
        return self.__handler

    @handler.setter
    def handler(self, handler):
        self.__handler = handler

    @property
    def gender(self):
        return self.__gender

    @gender.setter
    def gender(self, gender):
        self.__gender = gender

    @property
    def mouseline(self):
        return self.__mouseline

    @mouseline.setter
    def mouseline(self, mouseline):
        self.__mouseline = mouseline

    @property
    def genotype(self):
        return self.__genotype

    @genotype.setter
    def genotype(self, genotype):
        self.__genotype = genotype

    @property
    def birth_date(self):
        return self.__birth_date.strftime("%Y-%m-%d")

    @birth_date.setter
    def birth_date(self, birth_date):
        if isinstance(birth_date, datetime.date):
            self.__birth_date = birth_date
        else:
            self.__birth_date = datetime.datetime.strptime(birth_date, "%Y-%m-%d").date()

    @property
    def end_date(self):
        return self.__end_date.strftime("%Y-%m-%d")

    @end_date.setter
    def end_date(self, end_date):
        if isinstance(end_date, datetime.date):
            self.__end_date = end_date
        else:
            self.__end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    @property
    def cog(self):
        return self.__cog

    @cog.setter
    def cog(self, cog):
        self.__cog = cog

    @property
    def phenotype(self):
        return self.__phenotype

    @phenotype.setter
    def phenotype(self, phenotype):
        self.__phenotype = phenotype

    @property
    def project_title(self):
        return self.__project_title

    @project_title.setter
    def project_title(self, project_title):
        self.__project_title = project_title

    @property
    def experiment(self):
        return self.__experiment

    @experiment.setter
    def experiment(self, experiment):
        self.__experiment = experiment

    @property
    def comment(self):
        return self.__comment

    @comment.setter
    def comment(self, comment):
        self.__comment = comment

    @property
    def pfa_record(self):
        return self.__pfa_record

    @pfa_record.setter
    def pfa_record(self, pfa_record):
        self.__pfa_record = pfa_record if pfa_record is not None else AdvancedRecord()

    @property
    def freeze_record(self):
        return self.__freeze_record

    @freeze_record.setter
    def freeze_record(self, freeze_record):
        self.__freeze_record = freeze_record if freeze_record is not None else Record()

    def get_attribute_by_str(self, column_name):
        dict_self = self.__dict__
        return dict_self[column_name]


class Record:
    """
    Record class, contains the information regarding to the
    dissection information of the mouse
    """

    def __init__(self, liver=0, liver_tumor=0, others=''):
        self.liver = liver
        self.liver_tumor = liver_tumor
        self.others = others

    @property
    def liver(self):
        return self.__liver

    @liver.setter
    def liver(self, liver):
        try:
            self.__liver = int(liver)
        except ValueError:
            self.__liver = 0
    @property
    def liver_tumor(self):
        return self.__liver_tumor

    @liver_tumor.setter
    def liver_tumor(self, liver_tumor):
        try:
            self.__liver_tumor = int(liver_tumor)
        except ValueError:
            self.__liver_tumor = 0

    @property
    def others(self):
        return self.__others

    @others.setter
    def others(self, others):
        self.__others = others

    def __eq__(self, other):
        return self.liver == other.liver and \
               self.liver_tumor == other.liver_tumor and \
               self.others == other.others


class AdvancedRecord(Record):
    """
    Advanced Record, inhereited from Record with extened
    information
    """

    def __init__(self, liver=0, liver_tumor=0, small_intenstine=0,
                 small_intenstine_tumor=0, skin=0, skin_tumor=0, others=''):
        super().__init__(liver, liver_tumor, others)
        self.small_intenstine = small_intenstine
        self.small_intenstine_tumor = small_intenstine_tumor
        self.skin = skin
        self.skin_tumor = skin_tumor

    @property
    def small_intenstine(self):
        return self.__small_intenstine

    @small_intenstine.setter
    def small_intenstine(self, small_intenstine):
        try:
            self.__small_intenstine = int(small_intenstine)
        except ValueError:
            self.__small_intenstine = 0
    @property
    def small_intenstine_tumor(self):
        return self.__small_intenstine_tumor

    @small_intenstine_tumor.setter
    def small_intenstine_tumor(self, small_intenstine_tumor):
        try:
            self.__small_intenstine_tumor = int(small_intenstine_tumor)
        except ValueError:
            self.__small_intenstine_tumor = 0
    @property
    def skin(self):
        return self.__skin

    @skin.setter
    def skin(self, skin):
        try:
            self.__skin = int(skin)
        except ValueError:
            self.__skin = 0
    @property
    def skin_tumor(self):
        return self.__skin_tumor

    @skin_tumor.setter
    def skin_tumor(self, skin_tumor):
        try:
            self.__skin_tumor = int(skin_tumor)
        except ValueError:
            self.__skin_tumor = 0

    def __eq__(self, other):
        return self.liver == other.liver and \
               self.liver_tumor == other.liver_tumor and \
               self.small_intenstine == other.small_intenstine and \
               self.small_intenstine_tumor == other.small_intenstine_tumor and \
               self.skin == other.skin and \
               self.skin_tumor == other.skin_tumor and \
               self.others == other.others


"""
Helper function
"""


def is_list(input_check):
    """
    helper function to check if the given
    parameter is a list
    """
    return isinstance(input_check, list)


def check_content_type(input_check, type_check_func):
    """
    check if the given array or instance
    with the given type
    """
    if is_list(input_check):
        for m in input_check:
            if not type_check_func(m):
                return False
    else:
        if not type_check_func(input_check):
            return False

    return True


def check_if_mouse_type(input_check):
    return check_content_type(input_check, lambda x: isinstance(x, Mouse))
