from flask import Blueprint, request, jsonify
from models import Review, Person, Snack
from utils import token_required, validate_data


reviews_blueprint = Blueprint('reviews', __name__)

@reviews_blueprint.route('/reviews/create', methods=['POST'])
@token_required
def create_review(current_user_id):
    data = request.get_json()
    is_valid, error_message =validate_data(data, ['comment', 'snack_id'])
    if not is_valid:
        return jsonify({'message': error_message}), 400
    
    person = Person.nodes.get(uid=current_user_id)
    snack = Snack.nodes.get(uid=data['snack_id'])
    review = Review(comment=data['comment'])
    review.written_by.connect(person)
    snack.reviews.connect(review)
    review.save()
    return jsonify(review.to_dict()), 201



@reviews_blueprint.route('/reviews/delete/<uid>', methods=['POST'])
@token_required
def delete_review(current_user_id, uid):
    try:
        review = Review.nodes.get(uid=uid)
        review.delete()
        return jsonify({'message': 'Review deleted successfully'}), 200
    except Review.DoesNotExist:
        return jsonify({'message': 'Review not found'}), 404

@reviews_blueprint.route('/ratings', methods=['POST'])
@token_required
def add_rating(current_user_id):
    data = request.get_json()
    is_valid, error_message =validate_data(data, ['snack_id', 'rating'])
    if not is_valid:
        return jsonify({'message': error_message}), 400
    person = Person.nodes.get(uid=current_user_id)
    snack = Snack.nodes.get(uid=data['snack_id'])
    if person.rated.is_connected(snack):
        rated_rel = person.rated.relationship(snack)
        rated_rel.rating = data['rating']
        rated_rel.save()
    else:
        person.rated.connect(snack, {'rating': data['rating']})
    return jsonify({'message': 'Rating added successfully'}), 201
