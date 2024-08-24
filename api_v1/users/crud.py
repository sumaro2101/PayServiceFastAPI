from .schemas import CreateUser


def create_user(user: CreateUser):
    user = CreateUser.model_dump(user)
    return {
        'success': True,
        'user': user,
    }
