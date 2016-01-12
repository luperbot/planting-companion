"""Explaination of the garden object."""
import json


PLANT_FILE_JSON = 'plants.json'


def get_plant_data():
    with open(PLANT_FILE_JSON, 'r') as plantfile:
        plants = json.load(plantfile)
    return plants


class TooManyPlants(Exception):
    pass


class PlantDoesNotExist(Exception):
    pass


class Garden(object):
    PlantValues = get_plant_data()

    def __init__(self, length=1, width=1):
        """
        Set intial values for the garden.
        Total plot size is length * width, which limits the amount of plants choosen.
        """
        self.length = length
        self.width = width
        self.plot_size = length * width
        self.plants = {}
        self.plants_num = 0

    def clean_plant(self, plant_string):
        """Normalizes plant name and checks if plant values exist."""
        plant = plant_string.lower()
        plant_value = self.PlantValues.get(plant)
        if plant_value == None:
            raise PlantDoesNotExist(
                "No information about plant '%s' exists." % plant
                )
        return plant

    def add(self, plants):
        """
        Adds plants to the plants struct.
        Can be passed either a single string of plant name, or a list of
        plants/amount pair (ex. [('carrot', 1), ('pear', 3)]).
        """
        if type(plants) == list:
            for plant, amount in plants:
                self.add_plant(plant, amount=amount)
        else:
            self.add_plant(plants)
        return

    def add_plant(self, plant, amount=1):
        """
        Directly adds plants to plants struct.
        Do not use directly, use add_plants instead.
        Will raise error if plant doesn't exist or exceeds plot_size limit.
        """
        plant = self.clean_plant(plant)

        if self.plants_num + amount > self.plot_size:
            raise TooManyPlants(
                "Cannot add %s plants, exceeds plot size limit." % amount
                )

        current_amount = self.plants.get(plant, 0)
        self.plants[plant] = current_amount + amount
        self.plants_num += amount
        return

