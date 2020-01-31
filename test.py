from flaskblog import db, create_app
from flaskblog.models import User, Post, Comments

app = create_app()

db.init_app(app)
with app.app_context():
    db.create_all()

