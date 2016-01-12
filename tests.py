import unittest
from garden import Garden, TooManyPlants, PlantDoesNotExist

class TestGarden(unittest.TestCase):

    def setUp(self):
        self.length = 5
        self.width = 6
        self.garden = Garden(self.length, self.width)

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
        self.assertRaises(PlantDoesNotExist, self.garden.add, 'kitty-cat')

    def test_too_many_plants(self):
        for i in range(30):
            self.garden.add('leeks')
        self.assertRaises(TooManyPlants, self.garden.add, 'leeks')



