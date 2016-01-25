import time
import unittest

from plantingcompanion import exceptions, helpers, garden


class TestHelpers(unittest.TestCase):

    def test_get_plant_data(self):
        """Plant data should be loaded from plantingcompanion/plants.json file,
        and parsed correctly to be used by Garden objects.
        """
        plant_data = helpers.get_plant_data()

        # Current there are 68 plants in data.
        self.assertEqual(len(plant_data), 68)

    def test_permutations(self):
        """Permutations must return only unique combinations, excluding combinations
        that are mirrored (example: should not contain 'AB' and 'BA').
        """
        permutations_one = [('a', 'b', 'c'), ('a', 'c', 'b'), ('b', 'a', 'c')]
        permutations_two = [
            ('a', 'b'), ('a', 'c'), ('a', 'd'), ('b', 'c'), ('b', 'd'),
            ('c', 'd')
        ]

        self.assertEqual(
            permutations_one, list(helpers.permutations(['a', 'b', 'c']))
        )
        self.assertEqual(
            permutations_two, list(helpers.permutations('abcd', 2))
        )


class TestGarden(unittest.TestCase):

    def setUp(self):
        self.length = 6
        self.width = 5
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

    def test_plot_size(self):
        self.assertRaises(
            exceptions.InvalidPlot, garden.Garden, 3, 5
        )
        self.assertRaises(
            exceptions.InvalidPlot, garden.Garden, 3, 5
        )


class TestLayouts(unittest.TestCase):

    def compare_layout_with_estimate(self, plants, rows, columns):
        plot = garden.Plots()
        garden_plot = garden.Garden(rows, columns)
        garden_plot.add(plants)

        start = time.time()
        layout = garden_plot.find_layout()
        plot.set_plots(layout)
        score = plot.get_total_score()
        brute_time = time.time() - start

        start = time.time()
        layout_estimate = garden_plot.estimate_layout()
        plot.set_plots(layout_estimate)
        score_estimate = plot.get_total_score()
        estimate_time = time.time() - start

        print("")
        print("%s x %s" % (rows, columns))
        print(layout)
        print(layout_estimate)
        print("score: %s (%s secs) vs %s (%s secs)" % (
            score, brute_time, score_estimate, estimate_time
        ))

        return (layout, layout_estimate)

    def test_one(self):
        ideal_layout = [['corn']]
        plants = [('corn', 1)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 1, 1
        )
        self.assertEqual(ideal_layout, layout)

    def test_two(self):
        plants = [('corn', 1), ('garlic', 1)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 2, 1
        )

    def test_three(self):
        plants = [('corn', 2), ('garlic', 1)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 3, 1
        )

    def test_four(self):
        plants = [('corn', 2), ('garlic', 2)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 2, 2
        )

    def test_four_same(self):
        ideal_layout = [['corn', 'corn'], ['corn', 'corn']]
        plants = [('corn', 4)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 2, 2
        )
        self.assertEqual(ideal_layout, layout)

    def test_five(self):
        plants = [('corn', 2), ('garlic', 3)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 5, 1
        )

    def test_six(self):
        plants = [('corn', 2), ('garlic', 4)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 3, 2
        )

    def test_seven(self):
        plants = [('corn', 2), ('garlic', 1), ('beans', 4)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 7, 1
        )

    def test_eight(self):
        plants = [('corn', 4), ('garlic', 2), ('beans', 2)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 4, 2
        )

    def test_eight_same(self):
        ideal_layout = [
            ['corn', 'corn'],
            ['corn', 'corn'],
            ['corn', 'corn'],
            ['corn', 'corn'],
            ]
        plants = [('corn', 8)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 4, 2
        )
        self.assertEqual(ideal_layout, layout)

    def test_six_threepairs(self):
        plants = [('yarrow', 2), ('apple', 2), ('grass', 2)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 3, 2
        )

    def test_three_by_three(self):
        plants = [('yarrow', 5), ('apple', 2), ('grass', 2)]
        layout, layout_estimate = self.compare_layout_with_estimate(
            plants, 3, 3
        )

    def test_ten(self):
        if True:
            return
        plants = [('yarrow', 2), ('apple', 2), ('grass', 2), ('garlic', 4)]
        # layout, layout_estimate = self.compare_layout_with_estimate(
        #   plants, 5, 2
        # )

        plot = garden.Plots()
        garden_plot = garden.Garden(5, 2)
        garden_plot.add(plants)

        layout_estimate = garden_plot.estimate_layout()
        plot.set_plots(layout_estimate)
        score_estimate = plot.get_total_score()

        print("")
        print("Ten")
        print(layout_estimate)
        print(score_estimate)
