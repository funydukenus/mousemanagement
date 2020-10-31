from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from harvestmouseapp.mvc_model.model import MouseList, ColumnList


class FilterType(Enum):
    """
    This is the enumuration of the filter type which represents different method of filtering of mouse list
    """
    GTE = 0
    GT = 1
    LTE = 2
    LT = 3
    EQ = 4
    CONTAINS = 5


def get_enum_by_value(num):
    """
    This is the public function which represents the FilterType into index which provides easier and convienience
    way of representing the type of filter clients wishs to have
    """
    if num == 0:
        return FilterType.GTE
    elif num == 1:
        return FilterType.GT
    elif num == 2:
        return FilterType.LTE
    elif num == 3:
        return FilterType.LE
    elif num == 4:
        return FilterType.EQ
    else:
        return FilterType.CONTAINS


class FilterOption:
    """
    This class represents the filter option specified by the client including]
    1. The specific column the client wish the filter to depending on.
    2. The value of the criteria
    3. The way of the criteria to be compared with the data. i.e, GT, Greater than the value of the criteria
    """
    def __init__(self, column_name, value, filter_type=FilterType.CONTAINS):
        self.__column_name = ColumnList.header_name.value + column_name
        self.__value = value
        self.__filter_type = filter_type

    @property
    def column_name(self):
        return self.__column_name

    @column_name.setter
    def column_name(self, column_name):
        header_name = ColumnList.header_name.value
        self.__column_name = header_name + column_name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def filter_type(self):
        return self.__filter_type

    @filter_type.setter
    def filter_type(self, filter_type):
        self.__filter_type = filter_type


class GenericMouseFilter(ABC):
    """
    Expectes the subclass to implement the filter method to filter the mouse_input based on the
    filter option
    """
    @abstractmethod
    def filter(self, mouse_input, filter_option):
        pass


class MouseFilter(GenericMouseFilter):
    """
    This method filters the mouse list based on the filter option provided by the client.
    It will firstly fetch the entire mouse list and filter the mouse list filter option by
    filter option
    """
    def filter(self, mouse_input, filter_option):
        return_mouse_list = MouseList()
        value = filter_option.value
        col_name = filter_option.column_name

        if col_name == ColumnList.BIRTH_DATE.value or \
                col_name == ColumnList.END_DATE.value:
            value = datetime.strptime(value, "%Y-%m-%d").date()

        try:
            if filter_option.filter_type == FilterType.CONTAINS:
                list_mouse = [m for m in mouse_input if value in m.get_attribute_by_str(col_name)]
            elif filter_option.filter_type == FilterType.EQ:
                list_mouse = [m for m in mouse_input if value == m.get_attribute_by_str(col_name)]
            elif filter_option.filter_type == FilterType.GT:
                list_mouse = [m for m in mouse_input if value < m.get_attribute_by_str(col_name)]
            elif filter_option.filter_type == FilterType.GTE:
                list_mouse = [m for m in mouse_input if value <= m.get_attribute_by_str(col_name)]
            elif filter_option.filter_type == FilterType.LT:
                list_mouse = [m for m in mouse_input if value > m.get_attribute_by_str(col_name)]
            elif filter_option.filter_type == FilterType.LTE:
                list_mouse = [m for m in mouse_input if value >= m.get_attribute_by_str(col_name)]
            else:
                list_mouse = mouse_input
            return_mouse_list.add_mouse(list_mouse)
        except TypeError as e:
            list_mouse = mouse_input
            return_mouse_list.add_mouse(list_mouse)
        return return_mouse_list
