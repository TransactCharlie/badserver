from sanic import Sanic
from sanic import response
import asyncio
import assets


class BadServer:

    app = Sanic()

    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port

    def run(self):
        self.app.run(host=self.host, port=self.port)

    @app.route("/slowStream")
    async def slowStream(self):
        async def streaming_fn(response):
            response.write("start")
            for i in range(300):
                await asyncio.sleep(1)
                response.write(".")
            response.write("end")
        return response.stream(streaming_fn, content_type='text/plain')

    @app.route("/json")
    async def json(self):
        return response.json({"hellp": "world"})

    @app.route("/index.html")
    async def root(self):
        return response.html(assets.INDEXHTML)

    @app.route("/redirect_to_index")
    async def redirect(self):
        return response.redirect(to="/index.html", status=302)


if __name__ == '__main__':
    BadServer().run()
