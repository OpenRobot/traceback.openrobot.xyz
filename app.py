import typing
import fastapi
import asyncpg
import config
import uvicorn
from fastapi.responses import PlainTextResponse

class FastAPI(fastapi.FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pool: asyncpg.Pool = None

        self.add_event_handler('startup', self.on_startup)

    async def on_startup(self):
        self.pool = await asyncpg.create_pool(config.DATABASE_DSN)

app = FastAPI(title='OpenRobot Traceback', version='', docs_url=None, redoc_url=None, openapi_url=None, swagger_ui_oauth2_redirect_url=None)

@app.get('/{error_id}')
async def get_traceback(error_id: str, original: typing.Optional[bool] = False):
    if not app.pool:
        return PlainTextResponse('Currently Unavailable. Try again later.', status_code=503)

    try:
        while True:
            try:
                db = await app.pool.fetchrow('SELECT * FROM tracebacks WHERE error_id = $1', error_id)
            except asyncpg.exceptions._base.InterfaceError:
                pass
            else:
                break
    except:
        return PlainTextResponse('Error ID cannot be found.', status_code=404)

    if not db:
        return PlainTextResponse('Error ID cannot be found.', status_code=404)

    if original:
        return PlainTextResponse(db['traceback_original'])
    else:
        return PlainTextResponse(db['traceback_pretty'])

def run():
    uvicorn.run(app, host="127.0.0.1", port="3000")

run()