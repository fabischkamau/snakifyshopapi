from neomodel import StructuredNode,One, RelationshipFrom,UniqueIdProperty,StringProperty, DateTimeProperty, RelationshipTo, StructuredRel, OneOrMore, FloatProperty, BooleanProperty, IntegerProperty, ZeroOrOne, ArrayProperty
from neomodel import db


class Review(StructuredNode):
    uid = StringProperty(required=True)
    created_at = DateTimeProperty(default_now=True)
    comment = StringProperty(required=True)
    written_by = RelationshipTo("Person", "WRITTEN_BY", cardinality=OneOrMore)
    def to_dict(self):
        written_by = self.written_by.single()
        return {
            'uid': self.uid,
            'created_at': self.created_at.isoformat(),
            'comment': self.comment,
            'written_by': {
                'uid': written_by.uid,
                'first_name': written_by.first_name,
                'last_name': written_by.last_name
            }
        }

class ContainsRel(StructuredRel):
    added_at = DateTimeProperty(default_now=True)
    quantity_grams = IntegerProperty(required=True)


class Order(StructuredNode):
    uid = UniqueIdProperty()
    total = FloatProperty(required=True)
    created_at = DateTimeProperty(default_now=True)
    is_cancelled = BooleanProperty(default=False)
    contains = RelationshipTo("Snack", "CONTAINS", cardinality=OneOrMore, model=ContainsRel)
    payment_details = RelationshipTo('Transaction', 'PAYMENT_DATAILS', cardinality=One)
    status = StringProperty( choices={"pending": "pending", "completed": "completed"}, default="pending")
    
    def to_dict(self):
        snacks_data = []
        for rel in self.contains.all():
            snacks_data.append({
                'snack_id': rel.uid,
                'name': rel.name,
                'price_per_gram': rel.price_per_gram,
                'image_urls': rel.image_urls,
                'quantity_grams': db.cypher_query(f"MATCH (s:Snack {{uid: '{rel.uid}'}})<-[rel:CONTAINS]-(o:Order {{uid: '{self.uid}'}}) RETURN rel.quantity_grams AS quantity_grams")[0][0][0]
            })
        return {
            'uid': self.uid,
            'total': self.total,
            'created_at': self.created_at.isoformat(),
            'is_cancelled': self.is_cancelled,
            'snacks': snacks_data
        }
    

class RatedRel(StructuredRel):
    rating = FloatProperty(required=True)

class Person(StructuredNode):
    uid = UniqueIdProperty()
    first_name = StringProperty(required=True)
    phone = StringProperty(required=True, unique_index=True)
    email = StringProperty(unique_index=True)
    last_name = StringProperty(required=True)
    role = StringProperty(required=True, choices={"client": "client", "admin": "admin"})
    created_at = DateTimeProperty(default_now=True)
    password = StringProperty()
    rated = RelationshipTo("Snack", "RATED", cardinality=ZeroOrOne, model=RatedRel)
    orders_placed = RelationshipFrom('Order', 'PLACED')

    def to_dict(self):
        return {
            'uid': self.uid,
            'first_name': self.first_name,
            'phone': self.phone,
            'email': self.email,
            'last_name': self.last_name,
            'created_at': self.created_at.isoformat(),
        }


class Snack(StructuredNode):
    uid = UniqueIdProperty()
    price_per_gram = FloatProperty(required=True)
    description = StringProperty(required=True)
    name = StringProperty(index=True)
    created_at = DateTimeProperty(default_now=True)
    image_urls = ArrayProperty(StringProperty(),required=True)
    nutritional_content = StringProperty()
    in_order = RelationshipFrom('Order', 'CONTAINS', cardinality=OneOrMore, model=ContainsRel)
    

    def to_dict(self):
        return {
            'uid': self.uid,
            'price_per_gram': self.price_per_gram,
            'description': self.description,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'image_urls': self.image_urls,
            'nutritional_content': self.nutritional_content
        }


class Transaction(StructuredNode):
    uid = UniqueIdProperty()
    amount = FloatProperty(required=True)
    phone = StringProperty(required=True)
    method = StringProperty(required=True)
    created_at = DateTimeProperty(default_now=True)
    order = RelationshipTo("Order", "PAYMENT_DATAILS", cardinality=One)

    def to_dict(self):
        return {
            'uid': self.uid,
            'amount': self.amount,
            'phone': self.phone,
            'method': self.method,
            'created_at': self.created_at.isoformat(),
            'order_id': self.order.single().uid if self.order.single() else None
        }
