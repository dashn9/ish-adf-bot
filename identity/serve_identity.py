from aiohttp import web
import aiohttp_cors
import random

import asyncio
from threading import Thread


class ServeIdentity:

    def __init__(self, identity):
        # Setup CORS and application
        self.identity = identity
        self._app = web.Application(debug=True)
        self._cors = self.setup_cors()
        self.setup_routes()

    def setup_routes(self):
        resource = self._cors.add(self._app.router.add_resource("/"))
        self._cors.add(
            resource.add_route("GET", self.handle_get),
            {
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers=("X-Custom-Server-Header",),
                    allow_headers=("X-Requested-With", "Content-Type"),
                    max_age=3600,
                )
            },
        )

    def setup_cors(self):
        return aiohttp_cors.setup(self._app)

    async def handle_get(self, request):
        return web.json_response(self.get_identity_browser_data())

    def get_identity_browser_data(self):
        return {
            "fontWidthOffset": self.identity.font_fp_offset[0],
            "fontHeightOffset": self.identity.font_fp_offset[1],
            "hasBattery": self.identity.has_battery,
            "browser": self.identity.browser_name,
            "webglValueIndexSeed": self.identity.webgl_fp_offset[0],
            "webglValueOffset": self.identity.webgl_fp_offset[1],
            "audioContextOffset": self.identity.audio_context_fp_offset,
            "webglParam37445": self.identity.gpu_vendor,
            "webglParam37446": self.identity.gpu_renderer,
            "memory": self.identity.memory,
            "referrer": self.identity.referer,
            "canvasIndexes": self.identity.canvas_fp_offset,
            "windowHistoryCount": random.randint(0, 8),
        }

    def start_server(self, host="127.0.0.1", port=2370):
        def as_server(handler):
            print("======== Starting Identity Server For Browser ========")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            server = loop.create_server(handler, host=host, port=port)
            loop.run_until_complete(server)
            loop.run_forever()

        t = Thread(target=as_server, args=(self._app.make_handler(),))
        t.start()
