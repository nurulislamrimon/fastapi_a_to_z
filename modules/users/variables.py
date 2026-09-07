from modules.users.model import User

SEARCH_COLUMNS = [User.name, User.email]

FILTER_COLUMNS = {
    "name": User.name,
    "email": User.email,
}

SORT_COLUMNS = {
    "id": User.id,
    "name": User.name,
    "email": User.email,
}