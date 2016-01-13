import unittest
from plantingcompanion import garden
from plantingcompanion import exceptions


class TestGarden(unittest.TestCase):

    def setUp(self):
        self.length = 5
        self.width = 6
        self.garden = garden.Garden(self.length, self.width)

    def test_plot_size(self):
        """Plot size should equal length * width."""
        self.assertEqual(self.garden.plot_size, self.length * self.width)

    def test_add_plants(self):
        """Add 30 plants to the garden, via list add and by single plant."""
        plants = [
            ('radish', 5),
            ('corn', 5),
            ('garlic', 5),
            ('lettuce', 5),
            ('beans', 9)
        ]
        self.garden.add(plants)
        self.garden.add('beans')
        self.assertEqual(self.garden.plants_num, 30)

    def test_plant_does_not_exist(self):
        self.assertRaises(
            exceptions.PlantDoesNotExist, self.garden.add, 'kitty-cat'
            )

    def test_too_many_plants(self):
        for i in range(30):
            self.garden.add('leeks')
        self.assertRaises(exceptions.TooManyPlants, self.garden.add, 'leeks')


class TestPlots(unittest.TestCase):

    def setUp(self):
        garden_plot = [
            ['corn', 'corn', 'beans', 'beans'],
            ['corn', 'corn', 'beans', 'corn'],
            ['corn', 'lettuce', 'beans', 'corn'],
            ['corn', 'corn', 'corn', 'garlic'],
        ]
        self.plot = garden.Plots()
        self.plot.set_plots(garden_plot)

    def test_plot_dimentions(self):
        self.assertEqual(self.plot.rows, 4)
        self.assertEqual(self.plot.columns, 4)

    def test_coordinate_validity(self):
        self.assertRaises(
            exceptions.InvalidCoordinates, self.plot.get_plant, 8, 4
            )
        self.assertRaises(
            exceptions.InvalidCoordinates, self.plot.get_plant, 3, -4
            )
        self.assertRaises(
            exceptions.InvalidCoordinates, self.plot.get_plant, 3, 10
            )

    def test_get_plot(self):
        self.assertEqual(self.plot.get_plant(3, 3), 'garlic')

    def test_get_plot_score(self):
        self.assertEqual(self.plot.get_plot_score(3, 3), -10)

    def test_get_total_score(self):
        self.assertEqual(self.plot.get_total_score(), 20)


class TestLayouts(unittest.TestCase):

    def test_one(self):
        ideal_layout = [['corn']]
        garden_plot = garden.Garden(1, 1)
        garden_plot.add([('corn', 1)])
        layout = garden_plot.find_layout()
        self.assertEqual(ideal_layout, layout)

    def test_two(self):
        garden_plot = garden.Garden(1, 2)
        garden_plot.add([('corn', 1), ('garlic', 1)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_three(self):
        garden_plot = garden.Garden(1, 3)
        garden_plot.add([('corn', 2), ('garlic', 1)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_four(self):
        garden_plot = garden.Garden(2, 2)
        garden_plot.add([('corn', 2), ('garlic', 2)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_four_same(self):
        ideal_layout = [['corn', 'corn'], ['corn', 'corn']]
        garden_plot = garden.Garden(2, 2)
        garden_plot.add([('corn', 4)])
        layout = garden_plot.find_layout()
        self.assertEqual(ideal_layout, layout)

    def test_five(self):
        garden_plot = garden.Garden(1, 5)
        garden_plot.add([('corn', 2), ('garlic', 3)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_six(self):
        garden_plot = garden.Garden(2, 3)
        garden_plot.add([('corn', 2), ('garlic', 4)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_seven(self):
        garden_plot = garden.Garden(1, 7)
        garden_plot.add([('corn', 2), ('garlic', 1), ('beans', 4)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_eight(self):
        garden_plot = garden.Garden(2, 4)
        garden_plot.add([('corn', 4), ('garlic', 2), ('beans', 2)])
        layout = garden_plot.find_layout()
        print(layout)

    def test_eight_same(self):
        ideal_layout = [
            ['corn', 'corn', 'corn', 'corn'],
            ['corn', 'corn', 'corn', 'corn']
            ]
        garden_plot = garden.Garden(2, 4)
        garden_plot.add([('corn', 8)])
        layout = garden_plot.find_layout()
        self.assertEqual(ideal_layout, layout)
