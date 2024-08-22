from fastapi import Path, APIRouter

from typing import Annotated


router = APIRouter(prefix='/items',
                   tags=['products'],
                   )


@router.get('/')
def list_items():
    return [
        'Item1',
        'Item2',
    ]


@router.get('/{item_id}/')
def get_item_by_id(item_id: Annotated[int,
                                      Path(title='id предмета',
                                           description='id предмета',
                                           ge=1,
                                           )],
                   ) -> dict:
    return {
        'item': {
            "id": item_id,
        },
    }
