from harvestmouseapp.mvc_model.Error import WrongTypeError
from harvestmouseapp.mvc_model.model import MouseList, Mouse


class MouseController:
    """
    MouseContoller is a class which uses as the business controller logic to
    coordinate flow of the data in and out from the database and transforming of the representation of the mouse data
    by using the MouseModalAdapter and MouseModalViewer class
    It acts as the controller role in the MVC model.
    """

    def __init__(self):
        self._db_adapter = None
        self._mouse_viewer = None
        self._mouse_filter = None
        self._mouse_validator = None
        self._model_adapter = None

    def set_db_adapter(self, adapter):
        """
        # Sets the database adapter which controls the database accessbility
        """
        self._db_adapter = adapter

    def set_mouse_viewer(self, viewer):
        """
        Sets the mouse viewer which helps transform Mouse or MouseList object to external required data format
        """
        self._mouse_viewer = viewer

    def set_mouse_filter(self, mouse_filter):
        """
        Sets the mouse filter that helps filtered the mouse list based on the critiria given
        """
        self._mouse_filter = mouse_filter

    def set_model_adapter(self, model_adapter):
        """
        Sets the mouse adapter which helps transform specified external formats of data into Mouse or MouseList object
        """
        self._model_adapter = model_adapter

    def create_mouse(self, raw_data):
        """
        Transform the raw_data into Mouse object
        It's adapter responsibility to differentiate
        list of mouse and single mouse
        """
        converted_data = self._model_adapter.transform(raw_data)
        return self._db_adapter.create_mouse(converted_data)

    def update_mouse(self, raw_data):
        """
        Transform the raw_data into Mouse object
        It's adapter responsibility to differentiate
        list of mouse and single mouse
        """
        converted_data = self._model_adapter.transform(raw_data)
        return self._db_adapter.update_mouse(converted_data)

    def get_mouse_for_transfer(self, filter_option=None, force=False, transform=True, get_num=False, use_paginator=False, page_size=0, page_index=0):
        """
        Physical id can be None, string object or list object
        if raw_data is None, get full list of mouse
        filter option only apply to the list of mouse
        """
        filtered_moust_list = self._db_adapter.get_all_mouse()

        if transform:
            if filter_option is not None:
                # Filtered mouse list can ba a list of mouse or single individual mouse object
                for f in filter_option:
                    filtered_moust_list = self._mouse_filter.filter(filtered_moust_list, f)

                # transform will take either single moust object or list of object
                # and transforms to target format
            if isinstance(filtered_moust_list, MouseList):
                if len(filtered_moust_list) != 1:
                    if use_paginator:
                        filtered_moust_list = filtered_moust_list.paginatate(page_size, page_index)
                    if get_num:
                        raw_return_data = filtered_moust_list.get_size()
                    else:
                        raw_return_data = self._mouse_viewer.transform(filtered_moust_list)
                else:
                    mouse = filtered_moust_list[0]
                    if get_num:
                        raw_return_data = 1
                    else:
                        raw_return_data = self._mouse_viewer.transform(mouse)
            elif isinstance(filtered_moust_list, Mouse):
                raw_return_data = self._mouse_viewer.transform(filtered_moust_list)
            else:
                raise WrongTypeError()
        else:
            raw_return_data = filtered_moust_list

        return raw_return_data

    def delete_mouse(self, raw_data=None):
        """
        Givne the entire mouse or mouse list information in specified data format
        and deletes those specified mouse via the physical id
        """
        # Calling this function to init the mouse list if possible
        converted_data = self._model_adapter.transform(raw_data)  # MouseList object
        return self._db_adapter.delete_mouse(converted_data)

    def get_num_total_mouse(self):
        """
        This method delegates the works to the database adapter to retrive the total
        entries of the mouse in the current mouselist cache in the database controller
        """
        return self._db_adapter.get_all_mouse(force=True).get_size()
