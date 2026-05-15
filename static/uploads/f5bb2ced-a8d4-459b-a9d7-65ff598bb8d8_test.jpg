from app import db, Menu


def login(client):
    return client.post('/login', data={
        'username': 'admin',
        'password': '123'
    }, follow_redirects=True)


def test_add_menu(client):
    login(client)

    response = client.post('/admin/menu/add', data={
        'name': 'Pizza',
        'price': '100',
        'description': 'Ngon',
        'image': (open(__file__, 'rb'), 'test.jpg')
    }, follow_redirects=True)

    assert "Thêm món thành công" in response.data.decode('utf-8')


def test_edit_menu(client):
    login(client)

    m = Menu(name='Burger', price=50, description='Test', image='a.jpg')
    db.session.add(m)
    db.session.commit()

    response = client.post(f'/admin/menu/edit/{m.id}', data={
        'name': 'Burger Updated',
        'price': '60',
        'description': 'Updated',
        'image': (open(__file__, 'rb'), 'test.jpg')
    }, follow_redirects=True)

    assert "Cập nhật thành công" in response.data.decode('utf-8')


def test_delete_menu(client):
    login(client)

    m = Menu(name='Delete', price=30, description='Test', image='a.jpg')
    db.session.add(m)
    db.session.commit()

    response = client.get(f'/admin/menu/delete/{m.id}', follow_redirects=True)

    assert "Xoá thành công" in response.data.decode('utf-8')