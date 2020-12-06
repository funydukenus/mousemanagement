from abc import ABC, abstractmethod

from django.core.paginator import Paginator
from django.db import IntegrityError

from harvestmouseapp.models import HarvestedMouse, HarvestedBasedNumber, HarvestedAdvancedNumber
from harvestmouseapp.mvc_model.Error import DuplicationMouseError, MouseNotFoundError
from harvestmouseapp.mvc_model.model import Mouse, MouseList
from harvestmouseapp.mvc_model.mouseFilter import MouseFilter


class GenericDatabaseAdapter(ABC):
    """
    This is the generic Database Class.
    In order to provide database side interface with seamlessly interaction
    with the rest of the components, this class must be extended.
    This class is part of the MVC model
    1. Subclass must have the responsibility to convert respective
        information into mouse or mouse list object
    """

    @abstractmethod
    def create_mouse(self, mouse_input):
        pass

    @abstractmethod
    def update_mouse(self, mouse_input):
        pass

    @abstractmethod
    def get_all_mouse(self, filter_options=None, page_size=0, page_index=0):
        pass

    @abstractmethod
    def delete_mouse(self, mouse_input):
        pass

    @abstractmethod
    def get_distinct_data_list(self, column_name):
        pass

    @abstractmethod
    def get_total_num_entries(self):
        pass


def _update_internal_harvested_mouse_and_save_into_cache(single_mouse):
    """
    Function: _create_internal_harvested_mouse_and_save_into_cache
    Description:
        This function helps to get the database mouse obj from the database and
        replace all the attributes of the mouse model from the single_mouse Mouse obj
    Parameter: Mouse
    Return: None
    """
    mouse_data_from_db = HarvestedMouse.objects.get(physicalId=single_mouse.physical_id)
    mouse_data_from_db.handler = single_mouse.handler
    mouse_data_from_db.gender = single_mouse.gender
    mouse_data_from_db.mouseLine = single_mouse.mouseline
    mouse_data_from_db.genoType = single_mouse.genotype
    mouse_data_from_db.birthDate = single_mouse.birth_date
    mouse_data_from_db.endDate = single_mouse.end_date
    mouse_data_from_db.confirmationOfGenoType = single_mouse.cog
    mouse_data_from_db.phenoType = single_mouse.phenotype
    mouse_data_from_db.projectTitle = single_mouse.project_title
    mouse_data_from_db.experiment = single_mouse.experiment
    mouse_data_from_db.comment = single_mouse.comment

    # Save the mouse into the database
    mouse_data_from_db.save()

    freeze_record_db = HarvestedBasedNumber.objects.get(harvestedMouseId=mouse_data_from_db.id)

    freeze_record_db.liver = single_mouse.freeze_record.liver
    freeze_record_db.liverTumor = single_mouse.freeze_record.liver_tumor
    freeze_record_db.others = single_mouse.freeze_record.others

    freeze_record_db.save()

    pfa_record_db = HarvestedAdvancedNumber.objects.get(harvestedMouseId=mouse_data_from_db.id)

    pfa_record_db.liver = single_mouse.pfa_record.liver
    pfa_record_db.liverTumor = single_mouse.pfa_record.liver_tumor
    pfa_record_db.smallIntestine = single_mouse.pfa_record.small_intenstine
    pfa_record_db.smallIntestineTumor = single_mouse.pfa_record.small_intenstine_tumor
    pfa_record_db.skin = single_mouse.pfa_record.skin
    pfa_record_db.skinHair = single_mouse.pfa_record.skin_tumor
    pfa_record_db.others = single_mouse.pfa_record.others

    pfa_record_db.save()


def _convert_sqlite_db_mouse_object_and_save_into_cache(db_raw):
    """
    Function: _create_internal_harvested_mouse_and_save_into_cache
    Description:
        This function helps convert list of database-mouse obj read from database
        and added into current mouse_list cache
    Parameter: QuerySet
    Return: MouseList
    """
    mouse_list = MouseList()
    for r in db_raw:
        m = Mouse(physical_id=r.physicalId,
                  handler=r.handler,
                  gender=r.gender,
                  mouseline=r.mouseLine,
                  genotype=r.genoType,
                  birth_date=str(r.birthDate),
                  end_date=str(r.endDate),
                  cog=r.confirmationOfGenoType,
                  phenotype=r.phenoType,
                  project_title=r.projectTitle,
                  experiment=r.experiment,
                  comment=r.comment)

        freeze_record_db = HarvestedBasedNumber.objects.get(harvestedMouseId=r.id)

        m.freeze_record.liver = freeze_record_db.liver
        m.freeze_record.liver_tumor = freeze_record_db.liverTumor
        m.freeze_record.others = freeze_record_db.others

        pfa_record_db = HarvestedAdvancedNumber.objects.get(harvestedMouseId=r.id)

        m.pfa_record.liver = pfa_record_db.liver
        m.pfa_record.liver_tumor = pfa_record_db.liverTumor
        m.pfa_record.small_intenstine = pfa_record_db.smallIntestine
        m.pfa_record.small_intenstine_tumor = pfa_record_db.smallIntestineTumor
        m.pfa_record.skin = pfa_record_db.skin
        m.pfa_record.skin_tumor = pfa_record_db.skinHair
        m.pfa_record.others = pfa_record_db.others

        mouse_list.add_mouse(m)

    return mouse_list


def _create_internal_harvested_mouse_and_save_into_cache(single_mouse):
    """
    Function: _create_internal_harvested_mouse_and_save_into_cache
    Description:
        This function helps to convert Mouse object into database mouse object and
        save it into database
    Parameter: Mouse
    Return: None
    """
    db_mouse_object = HarvestedMouse(
        physicalId=single_mouse.physical_id,
        handler=single_mouse.handler,
        gender=single_mouse.gender,
        mouseLine=single_mouse.mouseline,
        genoType=single_mouse.genotype,
        birthDate=single_mouse.birth_date,
        endDate=single_mouse.end_date,
        confirmationOfGenoType=single_mouse.cog,
        phenoType=single_mouse.phenotype,
        projectTitle=single_mouse.project_title,
        experiment=single_mouse.experiment,
        comment=single_mouse.comment
    )

    # Save the mouse into the database
    db_mouse_object.save()

    db_mouse_object.freezeRecord.create(
        liver=single_mouse.freeze_record.liver,
        liverTumor=single_mouse.freeze_record.liver_tumor,
        others=single_mouse.freeze_record.others
    ).save()

    db_mouse_object.pfaRecord.create(
        liver=single_mouse.pfa_record.liver,
        liverTumor=single_mouse.pfa_record.liver_tumor,
        smallIntestine=single_mouse.pfa_record.small_intenstine,
        smallIntestineTumor=single_mouse.pfa_record.small_intenstine_tumor,
        skin=single_mouse.pfa_record.skin,
        skinHair=single_mouse.pfa_record.skin_tumor,
        others=single_mouse.freeze_record.others
    ).save()


def _convert_and_add_mouse_into_cache_if_possible(mouse_ojb, return_mouse_input):
    """
    Function: _convert_and_add_mouse_into_cache_if_possible
    Description:
        This function helps convert Mouse object to database-mouse object and save into
        the database. Already existed mouse will not be added and will add to return
        mouse input
    Parameter: MouseList/Mouse, MouseList
    Return: MouseList
    """
    try:
        # calling this to do the actual muscle work
        _create_internal_harvested_mouse_and_save_into_cache(mouse_ojb)
    except HarvestedMouse.DoesNotExist:
        return_mouse_input.add_mouse(mouse_ojb)
    except IntegrityError:
        return_mouse_input.add_mouse(mouse_ojb)


def _convert_and_update_mouse_into_cache_if_possible(mouse_ojb, return_mouse_input):
    """
    Function: _convert_and_update_mouse_into_cache_if_possible
    Description:
        This function helps convert Mouse object to database-mouse object and update the corresponding mouse obj
        the database. Non-existed mouse will not be added and will add to return
        mouse input
    Parameter: MouseList/Mouse, MouseList
    Return: MouseList
    """
    try:
        _update_internal_harvested_mouse_and_save_into_cache(mouse_ojb)
    except HarvestedMouse.DoesNotExist:
        return_mouse_input.add_mouse(mouse_ojb)


def _convert_and_delete_mouse_into_cache_if_possible(mouse_ojb, return_mouse_input):
    """
    Function: _convert_and_delete_mouse_into_cache_if_possible
    Description:
        This function helps convert Mouse object to database-mouse object and delete the corresponding mouse obj
        the database. Non-existed mouse will not be added and will add to return
        mouse input
    Parameter: MouseList/Mouse, MouseList
    Return: MouseList
    """
    try:
        mouse_data_from_db = HarvestedMouse.objects.get(physicalId=mouse_ojb.physical_id)
        mouse_data_from_db.delete()
    except HarvestedMouse.DoesNotExist:
        return_mouse_input.add_mouse(mouse_ojb)


def _get_distinct_data_list(column_name):
    """
    Function: _get_distinct_data_list
    Description:
        Physically getting the data from the database and use distinct to
        get the distinct value of the set
    Parameter: column name
    Return: QuerySet
    """
    data_list = HarvestedMouse.objects.order_by().values(column_name).distinct()
    return data_list


class GenericSqliteConnector(GenericDatabaseAdapter):
    def __init__(self):
        super(GenericSqliteConnector, self).__init__()

    def create_mouse(self, mouse_input):
        """
        Function: create_mouse
        Description:
            This is an override create_mouse method from GenericDatabaseAdapter that
            use to insert/create the new Mouse entry into database.
            It does the following things in sequence
            1. Check if the incoming mouse_input object is a Mouse object or MouseList object and
               handle it respectively.
            2. Checks through the current cached mouse list and insert those mice that not yet
               presented in the mouse list. Return a list of mice that are duplicated in the mouse
               list
        Parameter: MouseList/Mouse
        Return: MouseList
        """
        return_mouse_input = MouseList()  # This mouse list will be return as duplicated mouse list

        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                _convert_and_add_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            _convert_and_add_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        if len(return_mouse_input) != 0:
            raise DuplicationMouseError(return_mouse_input)

    def update_mouse(self, mouse_input):
        """
        Function: update_mouse
        Description:
            This is an override update_mouse method from GenericDatabaseAdapter that
            use to update the existing Mouse entry from the database.
            It does the following things in sequence
            1. Initialize the mouse list if it has not yet initialized
            2. Check if the incoming mouse_input object is a Mouse object or MouseList oject and
               handle it respectively.
            3. Checks through the current cached mouse list and insert those mice that already
               presented in the mouse list. Return a list of mice that are not existed in the mouse
               list
        Parameter: MouseList/Mouse
        Return: MouseList
        """
        return_mouse_input = MouseList()  # This mouse list will be return as mouse list of non-existed mice
        if isinstance(mouse_input, MouseList):
            # mouse_input is a MouseList obj
            for m in mouse_input:
                _convert_and_update_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            # mouse_input is a Mouse obj
            _convert_and_update_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        if len(return_mouse_input) != 0:
            raise MouseNotFoundError(return_mouse_input)

    def get_all_mouse(self, filter_options=None, page_size=0, page_index=0):
        """
        Function: get_all_mouse
        Description:
            This is an override get_all_mouse method from GenericDatabaseAdapter that
            retrieve the MouseList obj either from the database. Supposedly
            the mouse_list obj will mirroring the actual data in the database. When force
            is set to True, the existing mouse_list obj will be clear and replace with the newly
            read data in the database. The implemented class should make use of the filter option
            to filter the list got from the database and apply page option to get the particular
            range from the filtered list
        Parameter: FilterOption, Page size, Page Index
        Return: MouseList
        """

        # Get all the mouse list from the database first
        # Getting all mouse list is faster than querying with parameters
        filtered_mouse_list = HarvestedMouse.objects.all()
        if filter_options is not None:
            my_filter = {}
            for f in filter_options:
                filter_option_str = MouseFilter().construct_filter_string(f)
                my_filter[filter_option_str] = f.value
            # Applying filter to the list got from the database
            # filtered_mouse_list should be the type of query set
            filtered_mouse_list = filtered_mouse_list.filter(**my_filter)

        # if page size is not provided
        # provide everything back to the caller
        if not (page_size == 0):
            pages = Paginator(filtered_mouse_list, page_size)
            filtered_mouse_list = pages.page(page_index + 1).object_list
            return _convert_sqlite_db_mouse_object_and_save_into_cache(filtered_mouse_list)
        else:
            return _convert_sqlite_db_mouse_object_and_save_into_cache(filtered_mouse_list)

    def delete_mouse(self, mouse_input):
        """
        Function: delete_mouse
        Description:
            This is an override delete_mouse method from GenericDatabaseAdapter that
            use to delete the existing Mouse entry from the database.
            It does the following things in sequence
            1. Check if the incoming mouse_input object is a Mouse object or MouseList object and
               handle it respectively.
            2. Iterate through the MouseList given and delete the mouse from the database accordingly
               If target mouse to be deleted is not found, it will be added into the return mouse input
               and return those mouse that not found back to the caller
        Parameter: MouseList
        Return: MouseList
        """
        return_mouse_input = MouseList()  # This mouse list will be return as mouse list of non-existed mice

        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                _convert_and_delete_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            _convert_and_delete_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        if len(return_mouse_input) != 0:
            raise MouseNotFoundError(mouse_input)

    def get_distinct_data_list(self, column_name):
        """
        Function: get_distinct_data_list
        Description:
            This is an override get_distinct_data_list which gets the distinct value of the
            given column got from the database
        Parameter: column name
        Return: list
        """
        return [data[column_name] for data in _get_distinct_data_list(column_name)]

    def get_total_num_entries(self, filter_options=None):
        """
        Function: get_total_num_entries
        Description:
            This is an override get_total_num_entries which gets the total number of
            entries from the database after applying the filer option if applicable
        Parameter: filter_options
        Return: number of entries
        """
        filtered_mouse_list = HarvestedMouse.objects.all()
        if filter_options is not None:
            my_filter = {}
            for f in filter_options:
                filter_option_str = MouseFilter().construct_filter_string(f)
                my_filter[filter_option_str] = f.value
            return filtered_mouse_list.filter(**my_filter).count()
        else:
            return filtered_mouse_list.count()
