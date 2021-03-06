
from django.db import models
from django.db.models import Sum, F, Count
from django.db.models.query import QuerySet


class EquipmentItemManager(models.Manager):

    def get_total_weight(self, exercise: int) -> dict:
        """Return the cumulative weight for all equipment associated with a single exercise."""
        pass

    def get_total_count(self, exercise: int) -> dict:
        """Return the cumulative count of all equipment associated with a single exercise."""
        pass

class AmmoItemManager(models.Manager):

    def get_total_base_allowance_weight(self, exercise: int) -> dict:
        """Return the cumulative base allowance weight of all ammo types associated with all equipment across an exercise."""
        return self.get_queryset().filter(
            equipment__in=Equipment.objects.filter(
                equipmentitem__in=EquipmentItem.objects.filter(
                    exercise__in=Exercise.objects.filter(id=exercise)
                    )
                )
            ).aggregate(total_ammo_base_allowance=Sum(
                F('ammo__weight') * 
                F('ammo__ammoitem__base_allocation') *
                F('equipment__equipmentitem__quantity')
                )
            )


    def get_total_daily_assault_weight(self, exercise: int) -> dict:
        """Return the cumulative daily assault replenishment weight of all ammo types associated with all equipment across an exercise."""
        return self.get_queryset().filter(
            equipment__in=Equipment.objects.filter(
                equipmentitem__in=EquipmentItem.objects.filter(
                    exercise__in=Exercise.objects.filter(id=exercise)
                    )
                )
            ).aggregate(total_ammo_daily_assault=Sum(
                F('ammo__weight') * 
                F('ammo__ammoitem__daily_assault') *
                F('equipment__equipmentitem__quantity')
                )
            )

    def get_total_daily_sustain_weight(self, exercise: int) -> dict:
        """Return the cumulative daily sustain replenishment weight of all ammo types associated with all equipment across an exercise."""
        return self.get_queryset().filter(
            equipment__in=Equipment.objects.filter(
                equipmentitem__in=EquipmentItem.objects.filter(
                    exercise__in=Exercise.objects.filter(id=exercise)
                    )
                )
            ).aggregate(total_ammo_daily_sustain=Sum(
                F('ammo__weight') * 
                F('ammo__ammoitem__daily_sustain') *
                F('equipment__equipmentitem__quantity')
                )
            )


class CombatLoadManager(models.Manager):

    def combat_loads(self, equipment: int) -> dict:
        """Return a list of all Combat Loads for a particular weapon system."""
        pass


# ammo
class Ammo(models.Model):
    """A part to a Equipment."""

    name = models.CharField(max_length=50, help_text="The common name of the part.")
    weight = models.IntegerField(default=0, help_text="The weight of the part.")

    def __str__(self):
        return self.name


class AmmoItem(models.Model):
    """A reference to Ammo that will exist in an exercise edl."""

    ammo = models.ForeignKey(Ammo, on_delete=models.CASCADE)

    GROUND_COMBAT_ELEMENT = 'G'
    NON_GROUND_COMBAT_ELEMENT = 'N'

    UNIT_TYPES = [
        (GROUND_COMBAT_ELEMENT, 'Ground Combat Element'),
        (NON_GROUND_COMBAT_ELEMENT, 'Non-Ground Combat Element'),

    ]

    unit_type = models.CharField(
        max_length=1,
        choices=UNIT_TYPES,
        default=GROUND_COMBAT_ELEMENT,
    )

    base_allocation = models.PositiveIntegerField(default=0, help_text="The base combat load for this weapon and ammo combination.")
    daily_assault = models.PositiveIntegerField(default=0, help_text="The daily sustainment quantity.")
    daily_sustain = models.PositiveIntegerField(default=0, help_text="The daily sustainment quantity.")

    objects = AmmoItemManager()

    @property
    def name(self):
        return self.ammo.name

    def __str__(self):
        return self.name

        
# equipment
class Equipment(models.Model):
    """A peice of equipment may belong to multiple units and multiple exercises at once."""

    name = models.CharField(max_length=50, help_text="The common name of the equipment.")
    fuel_capacity = models.IntegerField(default=0, help_text="The total fuel capacity in gallons.")
    burn_rate = models.FloatField(default=0, help_text="The burn rate of fuel in gal/h.")
    weight = models.FloatField(default=0, help_text="The weight of the equipment in pounds.")
    combat_loads = models.ManyToManyField(
        AmmoItem,
        through='CombatLoad',
        through_fields=('equipment','ammoitem',),
        help_text="A list of equipment ammo that this equipment contains."
        )

    def __str__(self):
        return self.name


class EquipmentItem(models.Model):
    """A reference to equipment that will exist in an exercise edl."""

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)

    ASSAULT = 'AE'
    FOLLOW_ON = 'AFOE'

    PHASING_LOCATION = [
        (ASSAULT, 'Assault Element'),
        (FOLLOW_ON, 'Assault Follow-On Element'),

    ]

    phasing_location = models.CharField(
        max_length=4,
        choices=PHASING_LOCATION,
        default=ASSAULT,
        help_text="The location of the item in relation to the phasing."
    )

    quantity = models.PositiveIntegerField(default=0, help_text="The quantity of an item.")
    objects = EquipmentItemManager()

    def __str__(self):
        return self.equipment.name



class CombatLoad(models.Model):
    """A reference to teh combat load for a peice of equipment."""

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    ammoitem = models.ForeignKey(AmmoItem, on_delete=models.CASCADE)
    objects = CombatLoadManager()

    def __str__(self):
        return self.ammoitem.name

# unit
class Unit(models.Model):
    """A unit that is used to hold many persons and assets."""

    name = models.CharField(max_length=50, help_text="The name of the unit.")

    def __str__(self):
        return self.name
    

# exercise
class Exercise(models.Model):
    """A exercise will be the primary object, composed of other objects that are associated with the exercise."""

    name = models.CharField(max_length=128)
    equipments = models.ManyToManyField(EquipmentItem, through="ExerciseEdl", through_fields=('exercise', 'equipment'),)
    units = models.ManyToManyField(Unit)

    class Meta:
        base_manager_name = 'objects'

    def __str__(self):
        return self.name


class ExerciseEdl(models.Model):
    """Intermediate table for Exercises and Equipments assigning a quantity."""

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    equipment = models.ForeignKey(EquipmentItem, on_delete=models.CASCADE, related_name='gear')

    def __str__(self):
        return f"{self.exercise}  {self.unit}  {self.equipment} "



