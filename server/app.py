from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from server.models import db, Restaurant, Pizza, RestaurantPizza
from sqlalchemy.exc import IntegrityError

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)
    Migrate(app, db)

    @app.route('/restaurants', methods=['GET'])
    def get_restaurants():
        restaurants = Restaurant.query.all()
        return jsonify([r.to_dict(rules=("-restaurant_pizzas",)) for r in restaurants]), 200

    @app.route('/restaurants/<int:id>', methods=['GET'])
    def get_restaurant(id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant:
            return jsonify(restaurant.to_dict(rules=["restaurant_pizzas", "restaurant_pizzas.pizza"])), 200
        return jsonify({"error": "Restaurant not found"}), 404

    @app.route('/restaurants/<int:id>', methods=['DELETE'])
    def delete_restaurant(id):
        restaurant = db.session.get(Restaurant, id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

    @app.route('/pizzas', methods=['GET'])
    def get_pizzas():
        pizzas = Pizza.query.all()
        return jsonify([p.to_dict(rules=("-restaurant_pizzas",)) for p in pizzas]), 200
    
    @app.route('/restaurant_pizzas', methods=['POST'])
    def create_restaurant_pizza():
        data = request.get_json()
        try:
            rp = RestaurantPizza(
                price=data['price'],
                pizza_id=data['pizza_id'],
                restaurant_id=data['restaurant_id']
            )
            db.session.add(rp)
            db.session.commit()
            return jsonify(rp.to_dict(rules=["pizza", "restaurant"])), 201
        except (ValueError, IntegrityError):
            db.session.rollback()
            return jsonify({"errors": ["validation errors"]}), 400

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(port=5555, debug=True)
