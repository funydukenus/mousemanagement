from abc import ABC, abstractmethod

from harvestmouseapp.models import HarvestedMouse, HarvestedBasedNumber, HarvestedAdvancedNumber
from harvestmouseapp.mvc_model.Error import DuplicationMouseError, MouseNotFoundError
from harvestmouseapp.mvc_model.model import Mouse, MouseList

from django.core.cache import caches, InvalidCacheBackendError
from django.core.cache import cache

class GenericDatabaseAdapter(ABC):
    """
    This is the generic Database Class.
    In order to provide database side interface with seamlessly interaction
    with the rest of the compoenents, this class must be extended.
    This class is part of the MVC model
    1. Subclass must have the responsibility to convert respective
        information into mouse or moustlist object
    2. Subclass must maintain the cache of mouse list
    """

    def __init__(self):
        self._mouse_list = None
        self.get_from_cache()
        if self._mouse_list is None:
            cache.set('ml', MouseList())
            self.get_from_cache()

    @abstractmethod
    def create_mouse(self, mouse_input):
        pass

    @abstractmethod
    def update_mouse(self, mouse_input):
        pass

    @abstractmethod
    def get_all_mouse(self, force=False):
        pass

    @abstractmethod
    def delete_mouse(self, mouse_input):
        pass

    def save_to_cache(self):
        cache.set('ml', self._mouse_list)

    def get_from_cache(self):
        self._mouse_list = cache.get('ml')


class GenericSqliteConnector(GenericDatabaseAdapter):
    def __init__(self):
        super(GenericSqliteConnector, self).__init__()

        # Retrive the get_all_mouse and converted into Mouse List object
        self.has_initialized_list_mouse = False

    def create_mouse(self, mouse_input):
        """
        This is an overrided create_mouse method from GenericDatabaseAdapter that
        use to insert/create the new Mouse entry into database.
        It does the following things in sequence
        1. Initialize the mouse list if it has not yet intiailized
        2. Check if the incoming mouse_input object is a Mouse object or MouseList oject and
           handle it respectivly.
        3. Checks through the current cached mouse list and insert those mice that not yet
           presented in the mouse list. Return a list of mice that are duplicated in the mouse
           list
        """

        self._init_cache_mouse_list_if_possible()  # Calling this function to init the mouse list if possible

        return_mouse_input = MouseList()  # This mouse list will be return as duplicated mouse list

        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                self._convert_and_add_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            self._convert_and_add_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        self.save_to_cache()

        if len(return_mouse_input) != 0:
            raise DuplicationMouseError(return_mouse_input)

    def update_mouse(self, mouse_input):
        """
        This is an overrided update_mouse method from GenericDatabaseAdapter that
        use to update the existing Mouse entry from the database.
        It does the following things in sequence
        1. Initialize the mouse list if it has not yet intiailized
        2. Check if the incoming mouse_input object is a Mouse object or MouseList oject and
           handle it respectivly.
        3. Checks through the current cached mouse list and insert those mice that already
           presented in the mouse list. Return a list of mice that are not existed in the mouse
           list
        """
        self._init_cache_mouse_list_if_possible()  # Calling this function to init the mouse list if possible

        return_mouse_input = MouseList()  # This mouse list will be return as mouse list of non-existed mice
        if isinstance(mouse_input, MouseList):
            # mouse_input is a MouseList obj
            for m in mouse_input:
                self._convert_and_update_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            # mouse_input is a Mouse obj
            self._convert_and_update_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        self.save_to_cache()

        if len(return_mouse_input) != 0:
            raise MouseNotFoundError(return_mouse_input)

    def get_all_mouse(self, force=False):
        """
        This is an overrided get_all_mouse method from GenericDatabaseAdapter that
        retrive the MouseList obj either from cache or from the database. Supposely
        the moust_list obj will mirroring the actual data in the databse. When force
        is set to True, the existing mouse_list obj will be clear and replace with the newly
        read data in the database
        """
        # Get from cache again
        self.get_from_cache()
        if force or self._mouse_list.get_size() == 0:
            self._mouse_list.clear()
            mouse_data_from_db = HarvestedMouse.objects.all()
            self._convert_sqlite_db_mouse_object_and_save_into_cache(mouse_data_from_db)
            return self._mouse_list
        else:
            return self._mouse_list

    def delete_mouse(self, mouse_input):
        """
        This is an overrided delete_mouse method from GenericDatabaseAdapter that
        use to delete the existing Mouse entry from the database.
        It does the following things in sequence
        1. Initialize the mouse list if it has not yet intiailized
        2. Check if the incoming mouse_input object is a Mouse object or MouseList oject and
           handle it respectivly.
        3. Checks through the current cached mouse list and delete those mice that already
           presented in the mouse list. Return a list of mice that are not existed in the mouse
           list
        """
        self._init_cache_mouse_list_if_possible()  # Calling this function to init the mouse list if possible

        return_mouse_input = MouseList()  # This mouse list will be return as mouse list of non-existed mice

        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                self._convert_and_delete_mouse_into_cache_if_possible(
                    mouse_ojb=m, return_mouse_input=return_mouse_input)
        else:
            self._convert_and_delete_mouse_into_cache_if_possible(
                mouse_ojb=mouse_input, return_mouse_input=return_mouse_input)

        self.save_to_cache()

        if len(return_mouse_input) != 0:
            raise MouseNotFoundError(mouse_input)

    def _create_intermal_harvested_mouse_and_save_into_cache(self, single_mouse):
        """
        This function helps to convert Mouse object into databse mouse object and
        save it into database
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

        # Save the mouse into the databse
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

        # Update mouse list cache
        self._mouse_list.add_mouse(single_mouse)

    def _update_intermal_harvested_mouse_and_save_into_cache(self, single_mouse):
        """
        This function helps to get the databse mouse obj from the database and
        replace all the atrributes of the mouse model from the single_mouse Mouse obj
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

        # Save the mouse into the databse
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

        # Update mouse list cache
        self._mouse_list.update_mouse(single_mouse)

    def _convert_sqlite_db_mouse_object_and_save_into_cache(self, db_raw):
        """
        This function helps convert list of database-mouse obj read from database
        and added into current mouse_list cache
        """
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

            self._mouse_list.add_mouse(m)

    def _init_cache_mouse_list_if_possible(self, force=True):
        """
        This function helps to initialize the mouse list obj and mark it
        as intialized. So next time it won't intitialized again.
        """
        if not self.has_initialized_list_mouse:
            self.get_all_mouse(force)
            self.has_initialized_list_mouse = True
            self.save_to_cache()

    def _convert_and_add_mouse_into_cache_if_possible(self, mouse_ojb, return_mouse_input):
        """
        This function helps convert Mouse object to databse-mouse object and save into
        the database. Already existed mouse will not be added and will add to return
        mouse input
        """
        if not self._mouse_list.is_mouse_in_list(mouse_input=mouse_ojb, list_check_by_id=True):
            # calling this to do the actual muscle work
            self._create_intermal_harvested_mouse_and_save_into_cache(mouse_ojb)
        else:
            return_mouse_input.add_mouse(mouse_ojb)

    def _convert_and_update_mouse_into_cache_if_possible(self, mouse_ojb, return_mouse_input):
        """
        This function helps convert Mouse object to databse-mouse object and update the corresponding mouse obj
        the database. Non-existed mouse will not be added and will add to return
        mouse input
        """
        if self._mouse_list.is_mouse_in_list(physical_id=mouse_ojb.physical_id):
            self._update_intermal_harvested_mouse_and_save_into_cache(mouse_ojb)
        else:
            return_mouse_input.add_mouse(mouse_ojb)

    def _convert_and_delete_mouse_into_cache_if_possible(self, mouse_ojb, return_mouse_input):
        """
        This function helps convert Mouse object to databse-mouse object and delete the corresponding mouse obj
        the database. Non-existed mouse will not be added and will add to return
        mouse input
        """
        if self._mouse_list.is_mouse_in_list(physical_id=mouse_ojb.physical_id):
            mouse_data_from_db = HarvestedMouse.objects.get(physicalId=mouse_ojb.physical_id)
            mouse_data_from_db.delete()
            self._mouse_list.remove_mouse(mouse_ojb)
        else:
            return_mouse_input.add_mouse(mouse_ojb)
