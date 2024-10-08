import pytest
import datetime

from api_v1.auth.utils import (get_hash_user,
                               get_values_user,
                               check_user,
                               )


@pytest.mark.utils
class TestUtilsAuth:
    
    def test_values_user(self):
        username = 'test'
        email = 'test@gmail.com'
        create_date = datetime.datetime(year=2024,
                                        month=8,
                                        day=22,
                                        hour=23,
                                        minute=54,
                                        second=30)
        value = get_values_user(
            username=username,
            create_date=create_date,
            email=email,
        )
        assert value == 'test-2024-8-22-23-54-30-test@gmail.com'