from modules.users.model import User

SEARCH_COLUMNS = [User.name, User.email]

FILTER_COLUMNS = {
    "name": User.name,
    "email": User.email,
    "is_active": User.is_active,
}

RANGE_COLUMNS = {
    "age_gte": (User.age, "gte"),
    "age_lte": (User.age, "lte"),
    "created_from": (User.created_at, "gte"),
    "created_to": (User.created_at, "lte"),
}

SORT_COLUMNS = {
    "id": User.id,
    "name": User.name,
    "email": User.email,
    "age": User.age,
    "is_active": User.is_active,
    "created_at": User.created_at,
}