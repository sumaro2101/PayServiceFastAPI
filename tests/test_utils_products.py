import pytest
from api_v1.products.utils import add_params


@pytest.mark.utils()
class TestUtilsProducts:
    
    def test_add_params(self):
        target = {'some': 'some'}
        result = add_params(target=target,
                            id=44,
                            )
        assert result == dict(some='some', id=44)