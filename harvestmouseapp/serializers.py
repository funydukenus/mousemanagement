from rest_framework import serializers
from harvestmouseapp.models import HarvestedMouse
from harvestmouseapp.models import HarvestedBasedNumber
from harvestmouseapp.models import HarvestedAdvancedNumber


class HarvestedMouseSerializer(serializers.ModelSerializer):

    class Meta:
        model = HarvestedMouse
        fields = ['id', 'handler', 'physicalId', 'gender', 'mouseLine', 'genoType', 'birthDate', 'endDate',
                  'confirmationOfGenoType', 'phenoType', 'projectTitle', 'experiment', 'comment']


class HarvestedBasedNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = HarvestedBasedNumber
        fields = ['id', 'harvestedMouseId', 'liver', 'liverTumor', 'others']


class HarvestedAdvancedNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = HarvestedAdvancedNumber
        fields = ['id', 'harvestedMouseId', 'liver', 'liverTumor', 'smallIntestine', 'smallIntestineTumor',
                  'skin', 'skinHair', 'others']