from harvestmouseapp.mvc_model.model import Mouse, MouseList


class MouseController:
    """
    MouseContoller is a class which uses as the business controller logic to
    coordinate the database control and the representation of the mouse data.
    It acts as the controller role in the MVC model.
    """

    def __init__(self):
        self._db_adapter = None
        self._mouse_viewer = None
        self._mouse_filter = None
        self._mouse_validator = None
        self._model_adapter = None

    def set_db_adapter(self, adapter):
        self._db_adapter = adapter

    def set_mouse_viewer(self, viewer):
        self._mouse_viewer = viewer

    def set_mouse_filter(self, mouse_filter):
        self._mouse_filter = mouse_filter

    def set_model_adapter(self, model_adapter):
        self._model_adapter = model_adapter

    def create_mouse(self, raw_data):
        # Transform the raw_data into Mouse object
        # It's adapter responsibility to differentiate
        # list of mouse and single mouse
        converted_data = self._model_adapter.transform(raw_data)
        return self._db_adapter.create_mouse(converted_data)

    def update_mouse(self, raw_data):
        # Transform the raw_data into Mouse object
        # It's adapter responsibility to differentiate
        # list of mouse and single mouse
        converted_data = self._model_adapter.transform(raw_data)
        return self._db_adapter.update_mouse(converted_data)

    def get_mouse_for_transfer(self, raw_data=None, filter_option=None, force=False, transform=True):
        # Physical id can be None, string object or list object
        # if raw_data is None, get full list of mouse
        # filter option only apply to the list of mouse

        raw_return_data = None
        data_from_db = self._db_adapter.get_all_mouse(force)

        if data_from_db is not None and transform:
            # Filtered mouse list can ba a list of mouse or single individual mouse object
            filtered_moust_list = data_from_db # self._mouse_filter.filter(data_from_db, raw_data, filter_option)

            # transform will take either single moust object or list of object
            # and transforms to target format
            raw_return_data = self._mouse_viewer.transform(filtered_moust_list)

        if not transform:
            raw_return_data = data_from_db

        return raw_return_data

    def delete_mouse(self, raw_data=None):
        converted_data = self._model_adapter.transform(raw_data)
        return self._db_adapter.delete_mouse(converted_data)

    def get_num_total_mouse(self):
        return self._db_adapter.get_all_mouse().get_size()