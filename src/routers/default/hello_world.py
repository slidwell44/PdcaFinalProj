from fastapi import APIRouter

router = APIRouter(tags=['Default'])

@router.get(
    '/hello-world',
    description='Prints the message Hello World!',
)
async def hello_world():
    return {'message': 'Hello World!'}