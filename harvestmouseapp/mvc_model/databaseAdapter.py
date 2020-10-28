from abc import ABC, abstractmethod

from harvestmouseapp.models import HarvestedMouse, HarvestedBasedNumber, HarvestedAdvancedNumber
from harvestmouseapp.mvc_model.model import Mouse, MouseList


class GenericDatabaseAdapter(ABC):
    """
    This is the generic Database Class.
    In order to provide database side interface with seamly interaction
    with the rest of the compoenents, this class must be extended.
    This class is part of the MVC model
    1. Subclass must have the responsibility to convert respective
        information into mouse or moustlist object
    2. Subclass must maintain the cache of mouse list
    """

    def __init__(self):
        self._mouse_list = MouseList()

    @abstractmethod
    def create_mouse(self, mouse_input) -> Mouse:
        pass

    @abstractmethod
    def update_mouse(self, mouse_input) -> Mouse:
        pass

    @abstractmethod
    def get_all_mouse(self, force=False):
        pass

    @abstractmethod
    def delete_mouse(self, mouse_input):
        pass


class GenericSqliteConnector(GenericDatabaseAdapter):
    def __init__(self):
        super(GenericSqliteConnector, self).__init__()
        # Retrive the get_all_mouse and converted into Mouse List object

    def create_mouse(self, mouse_input) -> Mouse:
        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                if not self._mouse_list.is_mouse_in_list(mouse_input=m, list_check_by_id=True):
                    self._create_intermal_harvested_mouse_and_save_into_cache(m)
        else:
            if not self._mouse_list.is_mouse_in_list(mouse_input=mouse_input, list_check_by_id=True):
                self._create_intermal_harvested_mouse_and_save_into_cache(mouse_input)

        return mouse_input

    def update_mouse(self, mouse_input) -> Mouse:
        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                if self._mouse_list.is_mouse_in_list(physical_id=m.physical_id):
                    self._update_intermal_harvested_mouse_and_save_into_cache(m)
        else:
            if self._mouse_list.is_mouse_in_list(physical_id=mouse_input.physical_id):
                self._update_intermal_harvested_mouse_and_save_into_cache(mouse_input)

        return mouse_input

    def get_all_mouse(self, force=False):
        if force or self._mouse_list.get_size() == 0:
            self._mouse_list.clear()
            mouse_data_from_db = HarvestedMouse.objects.all()
            self._convert_sqlite_db_mouse_object_and_save_into_cache(mouse_data_from_db)
            return self._mouse_list
        else:
            return self._mouse_list

    def delete_mouse(self, mouse_input):
        if isinstance(mouse_input, MouseList):
            for m in mouse_input:
                if self._mouse_list.is_mouse_in_list(physical_id=m.physical_id):
                    mouse_data_from_db = HarvestedMouse.objects.get(physicalId=m.physical_id)
                    mouse_data_from_db.delete()
                    self._mouse_list.remove_mouse(m)
        else:
            if self._mouse_list.is_mouse_in_list(physical_id=mouse_input.physical_id):
                mouse_data_from_db = HarvestedMouse.objects.get(physicalId=mouse_input.physical_id)
                mouse_data_from_db.delete()
                self._mouse_list.remove_mouse(mouse_input)

    def _create_intermal_harvested_mouse_and_save_into_cache(self, single_mouse):
        q = HarvestedMouse(
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
            experiment='',
            comment=single_mouse.comment
        )

        # Save the mouse into the databse
        q.save()
        # To-Do Create PFA and Freeze record respectivility

        q.freezeRecord.create(
            liver=single_mouse.freeze_record.liver,
            liverTumor=single_mouse.freeze_record.liver_tumor,
            others=single_mouse.freeze_record.others
        ).save()

        q.pfaRecord.create(
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
        mouse_data_from_db.experiment = ''
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


