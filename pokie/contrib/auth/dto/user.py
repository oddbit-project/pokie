from rick_db import fieldmapper


@fieldmapper(tablename='user', pk='id_user')
class User:
    id = 'id_user'
    active='active'
    admin='admin'
    username = 'login'
    first_name = 'first_name'
    last_name = 'last_name'
    email = 'email'
    creation_date = 'creation_date'
    last_login = 'last_login'
    password = 'password'
    attributes = 'attributes'
