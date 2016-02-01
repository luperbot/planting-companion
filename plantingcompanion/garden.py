"""Explaination of the garden object."""
from copy import deepcopy
from numpy import matrix, hstack, vstack

from plantingcompanion import exceptions, helpers

PLANT_VALUES = helpers.get_plant_data()


def score_plot(layout):
    plot = Plots()
    plot.set_plots(layout)
    return plot.get_total_score()


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

    def update_plot_dimensions(self, plot):
        """
        Check that the plot is valid dimensions,
        and update the row and column count.
        """
        if not plot:
            self.rows = 0
            self.columns = 0
            return

        # Check to make sure all the rows are the same length.
        if not all(len(plot[0]) == len(row) for row in plot):
            raise exceptions.InvalidPlot("Plot rows must be the same size.")

        if len(plot) < len(plot[0]):
            raise exceptions.InvalidPlot(
                "Width of plot cannot be larger than length."
            )

        self.rows = len(plot)
        self.columns = len(plot[0])

    def set_plots(self, plot):
        """
        Set or update plot matrix.
        Ex. [
            ['apple', 'pear'],
            ['apple', 'apple'],
            ['pear', 'pear']
            ]
        """
        self.update_plot_dimensions(plot)
        self.plot = plot

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
        if width > length:
            raise exceptions.InvalidPlot(
                "Width of plot cannot be larger than length."
            )

        self.length = length
        self.width = width
        self.plot_size = length * width
        self.plants = {}
        self.plants_num = 0
        self.plot = Plots()

    def score_plot(self):
        return self.plot.get_total_score()

    def mark_plants_as_used(self, plants, used_plants):
        for row in used_plants:
            for plant in row:
                plants[plant] -= 1

    def combine_plots(self, main, side, horizontal=False):
        stack = hstack if horizontal else vstack

        combo_one = stack((side, main)).tolist()
        self.plot.set_plots(combo_one)
        combo_one_score = self.plot.get_total_score()

        combo_two = stack((main, side)).tolist()
        self.plot.set_plots(combo_two)
        combo_two_score = self.plot.get_total_score()

        if combo_one_score > combo_two_score:
            return combo_one
        return combo_two

    def estimate_layout(self, plants=None, rows=None, columns=None):
        if plants is None:
            plants = deepcopy(self.plants)
        if rows is None:
            rows = self.length
        if columns is None:
            columns = self.width

        if rows * columns <= 3:
            # Return best combo avaliable.
            layout = self.find_layout(plants, length=rows, width=columns)
            self.mark_plants_as_used(plants, layout)
            return layout

        cut = int(rows / 2)
        # Special case, do hstack instead of vstack.
        if rows == columns or (rows % 2 == 1 and columns % 2 == 0):
            horizontal = True
            main_rows = rows
            main_columns = columns - cut
            side_rows = rows
            side_columns = cut
        else:
            horizontal = False
            main_rows = rows - cut
            main_columns = columns
            side_rows = cut
            side_columns = columns

        return self.combine_plots(
            self.estimate_layout(plants, rows=main_rows, columns=main_columns),
            self.estimate_layout(plants, rows=side_rows, columns=side_columns),
            horizontal=horizontal
        )

    def find_layout(self, avaliable_plants=None, length=None, width=None):
        if avaliable_plants is None:
            avaliable_plants = self.plants
        if length is None:
            length = self.length
        if width is None:
            width = self.width

        plants = []
        plots = Plots()
        for k, v in avaliable_plants.items():
            plants.extend([k]*v)
        plot_scores = []
        for p in helpers.permutations(plants, length*width):
            plots.set_plots(
                matrix(p).reshape(length, width).tolist()
                )
            score = plots.get_total_score()
            plot_scores.append((score, p))

        best_plot = max(plot_scores)[1]
        return matrix(best_plot).reshape(length, width).tolist()

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
