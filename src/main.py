import uvicorn

from src import app
from src.routers import default_router, game_router

app.include_router(default_router)
app.include_router(game_router)

if __name__ == '__main__':
    uvicorn.run('src.main:app', host='0.0.0.0', port=8000)