from __future__ import division
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from OpenTripMap_API import get_destinations 
from utilities import *

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
      
    @app.route("/get_shortest_route", methods=["GET"])
    def get_shortest_route():
        destinations = get_destinations()
        data = create_data(destinations)
        addresses = data['addresses']
        API_key = data['API_key']
        distance_matrix = create_distance_matrix(data)
        
        data = create_data_model(distance_matrix)
        print(distance_matrix)
        # Create the routing index manager.
        manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                              data['num_vehicles'], data['depot'])

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        
        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            route_details = get_solution(manager, routing, solution)
        
        return jsonify({
          "success": True,
          "objective": route_details['objective'],
          "route_distance": route_details['route_distance'],
          "route_nodes": route_details['route_nodes']
        })
            

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request :("
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Sorry, couldn't find a resource matching your request :("
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Sorry, couldn't process your request :("
        }), 422

    @app.errorhandler(500)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Method not allowed"
        }), 500

    return app