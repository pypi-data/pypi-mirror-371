from __future__ import annotations
from typing import Optional, Callable, Literal
from aiohttp import web
from functools import wraps
from rubigram.models import Update, InlineMessage
from rubigram.method import Method
from rubigram.filters import Filter
from rubigram.state import StateManager
from datetime import datetime
import asyncio
import logging


logger = logging.getLogger(__name__)


class Client(Method):
    def __init__(self, token: str, endpoint: Optional[str] = None, host: str = "0.0.0.0", port: int = 8000):
        self.token = token
        self.endpoint = endpoint
        self.host = host
        self.port = port
        self.offset_id = None
        self.state = StateManager()
        self.routes = web.RouteTableDef()
        self.message_handlers = []
        self.inline_handlers = []
        super().__init__(token)

    def on_message(self, *filters: Filter):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(client: Client, update: Update):
                try:
                    combined_filter = filters[0] if filters else None
                    for filter in filters[1:]:
                        combined_filter = combined_filter & filter

                    if combined_filter is None or await combined_filter(update):
                        await func(client, update)
                        return True
                    return False
                except Exception as error:
                    logger.exception("Error {}: {}".format(func.__name__, error))

            self.message_handlers.append(wrapper)
            return func
        return decorator

    def on_inline_message(self, *filters: Filter):
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(client: Client, update: InlineMessage):
                try:
                    combined_filter = filters[0] if filters else None
                    for filter in filters[1:]:
                        combined_filter = combined_filter & filter

                    if combined_filter is None or await combined_filter(update):
                        await func(client, update)
                        return True
                    return False
                except Exception as error:
                    logger.exception("Error {}: {}".format(func.__name__, error))

            self.inline_handlers.append(wrapper)
            return func
        return decorator

    async def dispatch(self, update: Update, type: Literal["update", "inline_message"] = "update"):
        handlers = self.message_handlers if type == "update" else self.inline_handlers
        for handler in handlers:
            try:
                matched = await handler(self, update)
                if matched:
                    return
            except Exception as error:
                logger.exception(f"Dispatch Error in handler [ {handler.__name__} ] : {error}")

    async def updater(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.from_dict(data.get("inline_message", {}))
            event.client = self
            await self.dispatch(event, "inline_message")
        elif "update" in data:
            event = Update.from_dict(data.get("update", {}))
            event.client = self
            await self.dispatch(event)
        else:
            return

    async def set_endpoints(self):
        if self.endpoint:
            await self.update_bot_endpoint(f"{self.endpoint}/ReceiveUpdate", "ReceiveUpdate")
            await self.update_bot_endpoint(f"{self.endpoint}/ReceiveInlineMessage", "ReceiveInlineMessage")

    def run(self):
        if self.endpoint:
            @self.routes.post("/ReceiveUpdate")
            async def receive_update(request: web.Request):
                data = await request.json()
                await self.updater(data)
                return web.json_response({"status": "OK"})

            @self.routes.post("/ReceiveInlineMessage")
            async def receive_inline_message(request: web.Request):
                data = await request.json()
                await self.updater(data)
                return web.json_response({"status": "OK"})

            app = web.Application()
            app.add_routes(self.routes)

            async def on_startup(app):
                await self.set_endpoints()
                await self.state.start()
                await self.start()

            async def on_cleanup(app):
                await self.state.stop()
                await self.stop()

            app.on_startup.append(on_startup)
            app.on_cleanup.append(on_cleanup)
            web.run_app(app, host=self.host, port=self.port)

        else:
            async def polling():
                try:
                    await self.state.start()
                    while True:
                        try:
                            get_update = await self.get_update(100, self.offset_id)
                            if get_update.updates:
                                updates = get_update.updates
                                for update in updates:
                                    if update.type == "NewMessage":
                                        message_time = int(update.new_message.time)
                                    elif update.type == "UpdatedMessage":
                                        message_time = int(update.updated_message.time)
                                    else:continue

                                    now = int(datetime.now().timestamp())
                                    if message_time >= now or message_time + 2 >= now:
                                        if isinstance(update, Update):
                                            update.client = self
                                        await self.dispatch(update)

                                self.offset_id = get_update.next_offset_id
                        except Exception as error:
                            logger.exception("Polling Error : {}".format(error))
                            await asyncio.sleep(1)

                except:
                    pass
                finally:
                    await self.state.stop()
                    await self.stop()
            asyncio.run(polling())