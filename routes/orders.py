from flask import Blueprint, request, jsonify
from models import Order, Person, Snack
from utils import token_required

orders_blueprint = Blueprint('orders', __name__)

@orders_blueprint.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user_id):
    try:
        person = Person.nodes.get(uid=current_user_id)
        orders = person.orders_placed.all()
        return jsonify([order.to_dict() for order in orders]), 200
    except Person.DoesNotExist:
        return jsonify({'message': 'User not found'}), 404


@orders_blueprint.route('/orders/create', methods=['POST'])
@token_required
def create_order(current_user_id):
    data = request.get_json()

    # Fetch the current user
    try:
        person = Person.nodes.get(uid=current_user_id)
    except Person.DoesNotExist:
        return jsonify({'message': 'Unauthorized'}), 404

    # Create the order
    try:
        order = Order(total=data['total'])
        order.save()

        # Connect snacks to the order
        for snack_data in data['snacks']:
            try:
                snack = Snack.nodes.get(uid=snack_data['snack_id'])
            except Snack.DoesNotExist:
                order.delete()  # Rollback order creation
                return jsonify({'message': 'Snack not found'}), 404

            order.contains.connect(snack, {'quantity_grams': snack_data['quantity_grams']})

        # Connect the order to the person
        person.orders_placed.connect(order)

        return jsonify(order.to_dict()), 201

    except Exception as e:
        return jsonify({'message': 'An error occurred while creating the order', 'error': str(e)}), 500


@orders_blueprint.route('/orders/cancel/<uid>', methods=['DELETE'])
@token_required
def cancel_order(current_user_id, uid):
    try:
        order = Order.nodes.get(uid=uid)
        if order.is_cancelled:
            return jsonify({'message': 'Order already cancelled'}), 400
        order.is_cancelled = True
        order.save()
        return jsonify({'message': 'Order cancelled successfully'}), 200
    except Order.DoesNotExist:
        return jsonify({'message': 'Order not found'}), 404
