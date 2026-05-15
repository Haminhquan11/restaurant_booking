from app import Menu, db


def test_home_page(client):
    response = client.get('/')

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Restaurant" in html


def test_menu_page(client):
    response = client.get('/menu')

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Menu" in html


def test_reservation_page(client):
    response = client.get('/reserve')

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Đặt bàn" in html
    assert "<form" in html
    assert 'name="name"' in html
    assert 'name="phone"' in html
    assert 'name="date"' in html
    assert 'name="time"' in html


def test_login_page(client):
    response = client.get('/login')

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Đăng nhập" in html
    assert 'name="username"' in html
    assert 'name="password"' in html


def test_menu_show_item(client):

    with client.application.app_context():
        item = Menu(
            name='Pizza',
            price=100,
            description='Ngon',
            image='test.jpg'
        )

        db.session.add(item)
        db.session.commit()

    response = client.get('/menu')

    html = response.data.decode('utf-8')

    assert "Pizza" in html
    assert "100" in html
    assert "Ngon" in html


def test_admin_menu_requires_login(client):
    response = client.get('/admin/menu', follow_redirects=True)

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Đăng nhập" in html


def test_add_menu_page_requires_login(client):
    response = client.get('/admin/menu/add', follow_redirects=True)

    html = response.data.decode('utf-8')

    assert "Đăng nhập" in html