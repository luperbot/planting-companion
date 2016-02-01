#!/usr/bin/env python
"""
API endpoints to list, process, and return data for optimal garden layouts.
"""
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

from plantingcompanion import helpers, garden

PLANT_VALUES = helpers.get_plant_data()

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()


def set_garden_arguments():
    """
    Sets POST args for /garden API endpoint.
    """
    parser.add_argument('length', type=int, required=True)
    parser.add_argument('width', type=int, required=True)
    for plant in PLANT_VALUES.keys():
        parser.add_argument(plant, type=int, default=0)

set_garden_arguments()


class Plants(Resource):

    def get(self):
        """
        Returns a list of avaliable plants for gardening selection in
        alphabetical order.
        """
        plants = list(PLANT_VALUES.keys())
        plants.sort()
        return plants


class CreateGarden(Resource):

    def post(self):
        """
        Takes the following arguments:
            'length' (int) - required, must be larger or equal to width
            'width' (int) - required, must be smaller or equal to length
            plant_name (int) - number of plants select from PLANT_VALUES

        Return a dictionary with a suggested garden layout in an array
        matrix, as well as the score of the suggested garden layout.
        """
        plants = parser.parse_args()
        length = plants.pop('length', 0)
        width = plants.pop('width', 0)
        plant_count = sum(count for plant, count in plants.items())

        # Validate the dimensions of the plot, and check that the count
        # of plants given match the plot size.
        if width > length:
            abort(406, message="Width of plot cannot be larger than length.")
        if length * width != plant_count:
            abort(
                406,
                message="Plot size must match amount of plants selected."
            )

        # Generate a plot layout for given plants and plant counts.
        # Return both a suggested plot layout and score of the
        # suggested layout.
        garden_plot = garden.Garden(length, width)
        garden_plot.add(list(plants.items()))
        plot = garden_plot.estimate_layout()
        return {
            'score': garden.score_plot(plot),
            'plot': plot
        }


api.add_resource(Plants, '/plants')
api.add_resource(CreateGarden, '/garden')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
