def login(client, username='admin', password='123'):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_login_success(client):

    response = login(client)

    html = response.data.decode('utf-8')

    assert response.status_code == 200


def test_login_fail(client):

    response = login(client, 'admin', 'wrongpassword')

    html = response.data.decode('utf-8')


    assert "Sai tài khoản hoặc mật khẩu" in html or "Đăng nhập" in html


def test_logout(client):

    login(client)

    response = client.get('/logout', follow_redirects=True)

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Đã đăng xuất" in html


def test_admin_requires_login(client):

    response = client.get('/admin', follow_redirects=True)

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Đăng nhập" in html


def test_admin_access_after_login(client):

    login(client)

    response = client.get('/admin')

    html = response.data.decode('utf-8')

    assert response.status_code == 200
    assert "Admin" in html or "Dashboard" in html


def test_session_after_login(client):

    login(client)

    with client.session_transaction() as session:
        assert session['user'] == 'admin'