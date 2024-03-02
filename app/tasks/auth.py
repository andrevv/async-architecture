from jose import jwt


SECRET_KEY = "e6sxwwm0ewbp7ngguovbvbkc3d8bvtqd08"
ALGORITHM = "HS256"


def get_current_user(token: str):
    pass