from flask import Blueprint, request, jsonify
from models import Snack
from utils import token_required, admin_required
from utils import validate_data

snacks_blueprint = Blueprint('snacks', __name__)

@snacks_blueprint.route('/snacks', methods=['GET'])
def get_snacks():
    snacks = Snack.nodes.all()
    return jsonify([snack.to_dict() for snack in snacks]), 200

@snacks_blueprint.route('/snacks/<uid>', methods=['GET'])
def get_snack(uid):
    try:
        snack = Snack.nodes.get(uid=uid)
        return jsonify(snack.to_dict()), 200
    except Snack.DoesNotExist:
        return jsonify({'message': 'Snack not found'}), 404

@snacks_blueprint.route('/snacks/create', methods=['POST'])
@admin_required
def create_snack(current_user_id):
    data = request.get_json()
    is_valid, error_message =validate_data(data, ['price_per_gram', 'description', 'name', 'image_urls','nutritional_content'])
    if not is_valid:
        return jsonify({'message': error_message}), 400

    snack = Snack(
        price_per_gram=data['price_per_gram'],
        description=data['description'],
        name=data['name'],
        image_urls=data['image_urls'],
        nutritional_content=data.get('nutritional_content', '')
    )
    snack.save()
    return jsonify(snack.to_dict()), 201

@snacks_blueprint.route('/snacks/<uid>', methods=['PUT'])
@admin_required
def update_snack(current_user_id, uid):
    try:
        snack = Snack.nodes.get(uid=uid)
        data = request.get_json()
        snack.price_per_gram = data.get('price_per_gram', snack.price_per_gram)
        snack.description = data.get('description', snack.description)
        snack.name = data.get('name', snack.name)
        snack.image_urls = data.get('image_urls', snack.image_urls)
        snack.nutritional_content = data.get('nutritional_content', snack.nutritional_content)
        snack.save()
        return jsonify(snack.to_dict()), 200
    except Snack.DoesNotExist:
        return jsonify({'message': 'Snack not found'}), 404

@snacks_blueprint.route('/snacks/<uid>', methods=['DELETE'])
@admin_required
def delete_snack(current_user_id, uid):
    try:
        snack = Snack.nodes.get(uid=uid)
        snack.delete()
        return jsonify({'message': 'Snack deleted successfully'}), 200
    except Snack.DoesNotExist:
        return jsonify({'message': 'Snack not found'}), 404
