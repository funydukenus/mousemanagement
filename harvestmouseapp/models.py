from django.db import models


#####################################################################
# Class name: HarvestedMouse                                        #
# Description:                                                      #
#    This is the class includes all the basic attribute for a       #
#    harvested mouse record.                                        #
#####################################################################
class HarvestedMouse(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    handler = models.TextField()
    physicalId = models.TextField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    mouseLine = models.TextField()
    genoType = models.TextField()
    birthDate = models.DateField(auto_now_add=False)
    endDate = models.DateField(auto_now_add=False)
    confirmationOfGenoType = models.TextField()
    phenoType = models.TextField()
    projectTitle = models.TextField()
    experiment = models.TextField()
    comment = models.TextField()


#####################################################################
# Class name: harvestedBasedNumber                                  #
# Description:                                                      #
#    This is the base class of the harvested number of each portion #
#    of the mouse. All the attributes are in terms of number        #
#####################################################################
class HarvestedBasedNumber(models.Model):
    harvestedMouseId = models.ForeignKey(HarvestedMouse, related_name='freezeRecord', on_delete=models.CASCADE)
    liver = models.IntegerField()
    liverTumor = models.IntegerField()
    others = models.TextField()


#####################################################################
# Class name: HarvestedAdvancedNumber                               #
# Description:                                                      #
#    This class inherits the basic attributes from the harvested    #
#    based number class. It has 4 other extra attributes. All       #
#    attributes are in terms of number                              #
#####################################################################
class HarvestedAdvancedNumber(models.Model):
    harvestedMouseId = models.ForeignKey(HarvestedMouse, related_name='pfaRecord', on_delete=models.CASCADE)
    liver = models.IntegerField()
    liverTumor = models.IntegerField()
    smallIntestine = models.IntegerField()
    smallIntestineTumor = models.IntegerField()
    skin = models.IntegerField()
    skinHair = models.IntegerField()
    others = models.TextField()
