"""Explaination of the garden object."""
import json
from numpy import matrix
from plantingcompanion import exceptions

PLANT_FILE_JSON = 'plantingcompanion/plants.json'


def get_plant_data():
    """
    Load JSON data from plants.
    Map plant values to each key.
    Friendly plants get +10 points, harmful plants get -10 points,
    and similar plants get -5 points.
    """
    with open(PLANT_FILE_JSON, 'r') as plantfile:
        plants = json.load(plantfile)

    plant_values = {}
    for plant, values in plants.items():
        plant_values[plant] = {plant: -5}
        plant_values[plant].update(
            {friend: 10 for friend in values['friends']}
        )
        plant_values[plant].update(
            {foe: -10 for foe in values['foes']}
        )
    return plant_values

PLANT_VALUES = get_plant_data()


class Plots(object):
    """
    Each plot is a matrix of nested arrays.
    X value is associated with rows, Y value is associated with columns.
    Coordinates follow:
                    y (col)
                (0, 0)      (0, y+n)
        x (row)
                (x+n, 0)    (x+n, y+n)
    Plots must be rectangular.
    """
    PlantValues = PLANT_VALUES

    def __init__(self, plot=None):
        self.plot = plot
        self.set_plots(plot)

    def update_plot_dimensions(self):
        """
        Check that the plot is valid dimensions,
        and update the row and column count.
        """
        if not self.plot:
            self.rows = 0
            self.columns = 0
            return

        # Check to make sure all the rows are the same length.
        if not all(len(self.plot[0]) == len(row) for row in self.plot):
            raise exceptions.InvalidPlot("Plot rows must be the same size.")
        self.rows = len(self.plot)
        self.columns = len(self.plot[0])

    def set_plots(self, plot):
        """
        Set or update plot matrix.
        Ex. [
            ['apple', 'pear'],
            ['apple', 'apple'],
            ['pear', 'pear']
            ]
        """
        self.plot = plot
        self.update_plot_dimensions()

    def check_coordinates(self, x, y):
        if x < 0 or y < 0:
            raise exceptions.InvalidCoordinates(
                "Coordinates must be positive integers."
                )
        if x >= self.rows:
            raise exceptions.InvalidCoordinates("X-axis exceeds plot width.")
        if y >= self.columns:
            raise exceptions.InvalidCoordinates("Y-axis exceeds plot length.")

    def _get_neighbors(self, x, y):
        top_row = max(x-1, 0)
        start_column = max(y-1, 0)

        for row in range(top_row, x+1):
            for column in range(start_column, y+1):
                if row != x and column != y:
                    yield self.plot[row][column]

    def get_plant(self, x, y):
        """
        Return plant type for (x, y) coordinate pair.
        """
        self.check_coordinates(x, y)
        return self.plot[x][y]

    def get_plot_score(self, x, y):
        self.check_coordinates(x, y)
        score = 0
        neighbors = list(self._get_neighbors(x, y))
        current_plant = self.get_plant(x, y)
        for plant in neighbors:
            score += self.PlantValues.get(plant, {}).get(current_plant, 0)
        return score

    def get_total_score(self):
        score = 0
        for x in range(self.rows):
            for y in range(self.columns):
                score += self.get_plot_score(x, y)
        return score


class Garden(object):
    PlantValues = PLANT_VALUES

    def __init__(self, length=1, width=1):
        """
        Set intial values for the garden.
        Total plot size is length * width,
        which limits the amount of plants choosen.
        """
        self.length = length
        self.width = width
        self.plot_size = length * width
        self.plants = {}
        self.plants_num = 0
        self.plot = Plots()

    def score_plot(self):
        return self.plot.get_total_score()

    def best_neighbors(self, plants_list, groups=None, x=1, y=2):
        if groups is None:
            groups = []

        if len(plants_list) == 1:
            plant = plants_list.keys()[0]
            return matrix([plant] * (x*y)).reshape(x, y).tolist()

        # Based on plot_size, determine how many pairs are needed.
        num_of_pairs = self.plot_size / (x*y)
        # TODO: Create all the pairing types possible.
        # TODO: Return the best ones.
        return [num_of_pairs]

    def find_layout(self):
        return self.best_neighbors(self.plants, x=self.length, y=self.width)

    def clean_plant(self, plant_string):
        """Normalizes plant name and checks if plant values exist."""
        plant = plant_string.lower()
        plant_value = self.PlantValues.get(plant)
        if plant_value is None:
            raise exceptions.PlantDoesNotExist(
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

    def add_plant(self, plant, amount=1):
        """
        Directly adds plants to plants struct.
        Do not use directly, use add_plants instead.
        Will raise error if plant doesn't exist or exceeds plot_size limit.
        """
        plant = self.clean_plant(plant)

        if self.plants_num + amount > self.plot_size:
            raise exceptions.TooManyPlants(
                "Cannot add %s plants, exceeds plot size limit." % amount
                )

        current_amount = self.plants.get(plant, 0)
        self.plants[plant] = current_amount + amount
        self.plants_num += amount
