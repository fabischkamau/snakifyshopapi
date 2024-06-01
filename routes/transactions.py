from flask import Blueprint, request, jsonify
from models import Transaction
from utils import token_required, admin_required, validate_data
from models import Order

transactions_blueprint = Blueprint('transactions', __name__)

@transactions_blueprint.route('/transactions', methods=['GET'])
@admin_required
def get_transactions(current_user_id):
    transactions = Transaction.nodes.all()
    return jsonify([transaction.to_dict() for transaction in transactions]), 200

from flask import request

@transactions_blueprint.route('/transactions/create', methods=['POST'])
@token_required
def create_transaction(current_user_id):
    data = request.get_json()

    is_valid, error_message =validate_data(data, ['amount', 'phone', 'method', 'order_uid'])
    if not is_valid:
        return jsonify({'message': error_message}), 400 

    try:
        # Retrieve the order UID from the request data
        order_uid = data.get('order_uid')

        # Fetch the order
        order = Order.nodes.get(uid=order_uid)

        # Create the transaction
        transaction = Transaction(
            amount=data['amount'],
            phone=data['phone'],
            method=data['method']
        )
        transaction.save()

        # Connect the transaction to the order
        order.payment_details.connect(transaction)
        order.status = 'completed'
        order.save()

        return jsonify({'message': 'Transaction created successfully'}), 201

    except Order.DoesNotExist:
        return jsonify({'error': 'Order not found'}), 404
