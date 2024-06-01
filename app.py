from flask import Flask
from flask_cors import CORS
from routes.auth import auth_blueprint
from routes.snacks import snacks_blueprint
from routes.orders import orders_blueprint
from routes.reviews import reviews_blueprint
from routes.transactions import transactions_blueprint
from routes.user import users_blueprint

app = Flask(__name__)
app.config.from_object('config')
CORS(app)

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(snacks_blueprint)
app.register_blueprint(orders_blueprint)
app.register_blueprint(reviews_blueprint)
app.register_blueprint(transactions_blueprint)
app.register_blueprint(users_blueprint)
@app.route('/')
def hello_world():
    return 'Snakify Api'
 

if __name__ == '__main__':
    app.run(debug=True)
