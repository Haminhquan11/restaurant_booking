import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import app, db, Reservation
from datetime import datetime, date


import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()


# ================= TEST ĐẶT BÀN =================

def test_valid_reservation(client):
    response = client.post('/reserve', data={
        'name': 'Test',
        'email': 'test@gmail.com',
        'phone': '123',
        'guests': '4',
        'date': date.today().strftime("%Y-%m-%d"),
        'time': '18:00',
        'table_number': '1'
    }, follow_redirects=True)

    assert "Đặt bàn thành công" in response.data.decode('utf-8')


def test_invalid_time(client):
    response = client.post('/reserve', data={
        'name': 'Test',
        'email': 'test@gmail.com',
        'phone': '123',
        'guests': '4',
        'date': date.today().strftime("%Y-%m-%d"),
        'time': '10:00',
        'table_number': '1'
    }, follow_redirects=True)

    assert "Đặt bàn không thành công" in response.data.decode('utf-8')


def test_invalid_guests(client):
    response = client.post('/reserve', data={
        'name': 'Test',
        'email': 'test@gmail.com',
        'phone': '123',
        'guests': '20',
        'date': date.today().strftime("%Y-%m-%d"),
        'time': '18:00',
        'table_number': '1'
    }, follow_redirects=True)

    assert "1-10 người" in response.data.decode('utf-8')


def test_past_date(client):
    response = client.post('/reserve', data={
        'name': 'Test',
        'email': 'test@gmail.com',
        'phone': '123',
        'guests': '4',
        'date': '2020-01-01',
        'time': '18:00',
        'table_number': '1'
    }, follow_redirects=True)

    assert "quá khứ" in response.data.decode('utf-8')


def test_duplicate_table(client):
    # đặt lần 1
    client.post('/reserve', data={
        'name': 'A',
        'email': 'a@gmail.com',
        'phone': '123',
        'guests': '4',
        'date': date.today().strftime("%Y-%m-%d"),
        'time': '18:00',
        'table_number': '2'
    })

    # đặt trùng
    response = client.post('/reserve', data={
        'name': 'B',
        'email': 'b@gmail.com',
        'phone': '456',
        'guests': '4',
        'date': date.today().strftime("%Y-%m-%d"),
        'time': '18:00',
        'table_number': '2'
    }, follow_redirects=True)

    data = response.data.decode('utf-8').lower()
    assert "đã có người đặt" in data


# ================= TEST ADMIN =================

def test_admin_login_required(client):
    response = client.get('/admin', follow_redirects=True)
    assert b"login" in response.data.lower()