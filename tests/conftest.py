import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


os.environ['TESTING'] = '1'

import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        admin = User(username='admin')
        admin.set_password('123')
        db.session.add(admin)
        db.session.commit()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()