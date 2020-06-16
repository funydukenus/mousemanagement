from rest_framework import serializers
from harvestmouseapp.models import HarvestedMouse
from harvestmouseapp.models import HarvestedBasedNumber
from harvestmouseapp.models import HarvestedAdvancedNumber


class HarvestedBasedNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestedBasedNumber
        fields = ['id', 'liver', 'liverTumor', 'others']

    """
    Override the create method to extract the corresponding
    of harvested mouse from the validated_data
    """
    def create(self, validated_data):
        harvested_mouse = HarvestedMouse.objects.get(physicalId=self.initial_data['physicalId'])

        return HarvestedBasedNumber.objects.create(
                harvestedMouseId=harvested_mouse,
                **validated_data)


class HarvestedAdvancedNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = HarvestedAdvancedNumber
        fields = ['id', 'liver', 'liverTumor', 'smallIntestine', 'smallIntestineTumor',
                  'skin', 'skinHair', 'others']

    """
    Override the create method to extract the corresponding
    of harvested mouse from the validated_data
    """
    def create(self, validated_data):
        harvested_mouse = HarvestedMouse.objects.get(physicalId=self.initial_data['physicalId'])

        return HarvestedAdvancedNumber.objects.create(
                harvestedMouseId=harvested_mouse,
                **validated_data)


class HarvestedMouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestedMouse
        fields = ['id', 'handler', 'physicalId', 'gender', 'mouseLine', 'genoType', 'birthDate', 'endDate',
                  'confirmationOfGenoType', 'phenoType', 'projectTitle', 'experiment', 'comment']

    def to_representation(self, instance):
        # Call the super to transform model to Harvested Mouse representation
        data = super(HarvestedMouseSerializer, self).to_representation(instance)

        # Get the corresponding harvest based number object
        # by using the instance id
        freeze_record = HarvestedBasedNumber.objects.get(harvestedMouseId=instance.id)

        # Convert the model of freeze_record into Json format
        harvested_based_number_serializer = HarvestedBasedNumberSerializer(freeze_record)
        data['freezeRecord'] = harvested_based_number_serializer.data

        # Get the corresponding harvest advanced number object
        # by using the instance id
        pfa_record = HarvestedAdvancedNumber.objects.get(harvestedMouseId=instance.id)

        # Convert the model of freeze_record into Json format
        harvested_advanced_number_serializer = HarvestedAdvancedNumberSerializer(pfa_record)
        data['pfaRecord'] = harvested_advanced_number_serializer.data

        return data

    """
    Override the create method to extract the corresponding
    of harvested mouse from the validated_data
    """
    def create(self, validated_data):
        harvested_mouse = HarvestedMouse.objects.create(**validated_data)

        if not isinstance(self.initial_data, list):
            number_serializer_assign_and_save('pfaRecord', self.initial_data)
            number_serializer_assign_and_save('freezeRecord', self.initial_data)
        else:
            for item in self.initial_data:
                if item['physicalId'] == harvested_mouse.physicalId:
                    number_serializer_assign_and_save('pfaRecord', item)
                    number_serializer_assign_and_save('freezeRecord', item)
                    break

        return harvested_mouse

    """
    Override the update method to extract the corresponding
    of harvested mouse from the validated_data
    """
    def update(self, instance, validated_data):
        edited_mouse = super(HarvestedMouseSerializer, self).update(instance, validated_data)
        if not isinstance(self.initial_data, list):
            number_serializer_assign_and_update('pfaRecord', edited_mouse, self.initial_data)
            number_serializer_assign_and_update('freezeRecord', edited_mouse, self.initial_data)
        else:
            for item in self.initial_data:
                if item['physicalId'] == edited_mouse.physicalId:
                    number_serializer_assign_and_update('pfaRecord', edited_mouse, item)
                    number_serializer_assign_and_update('freezeRecord', edited_mouse, item)
                    break
        return edited_mouse


def number_serializer_assign_and_save(typename, data):
    raw_data = data[typename]
    if typename == 'pfaRecord':
        serializer = HarvestedAdvancedNumberSerializer(data=raw_data)
    elif typename == 'freezeRecord':
        serializer = HarvestedBasedNumberSerializer(data=raw_data)
    if serializer.is_valid():
        serializer.save()


def number_serializer_assign_and_update(typename, target_edited_mouse, data):
    raw_data = data[typename]
    if typename == 'pfaRecord':
        instance = HarvestedAdvancedNumber.objects.get(harvestedMouseId=target_edited_mouse.id)
        serializer = HarvestedAdvancedNumberSerializer(instance, data=raw_data)
    elif typename == 'freezeRecord':
        instance = HarvestedBasedNumber.objects.get(harvestedMouseId=target_edited_mouse.id)
        serializer = HarvestedBasedNumberSerializer(instance, data=raw_data)
    if serializer.is_valid():
        serializer.save()
