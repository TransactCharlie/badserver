from sanic import Sanic
from sanic import response
import asyncio
from multiprocessing import Process
import click


DEFAULT_CERT = {"cert": "certs/host.cert", "key": "certs/host.key"}


class BadServer:

    app_http = Sanic()
    app_https = Sanic()
    https_process = None
    http_process = None

    def __init__(self, host="0.0.0.0", http_port=8000, https_port=8001, ssl_certs=DEFAULT_CERT):
        self.host = host
        self.http_port = http_port
        self.https_port = https_port
        self.ssl_certs = ssl_certs
        self.generate_index()
        self.generate_https_only_index()

    def run(self):
        http_args = {"port": self.http_port, "host": self.host}
        self.http_process = Process(target=self.app_http.run, kwargs=http_args)
        self.http_process.start()

        self.app_https.run(host=self.host, port=self.https_port, ssl=self.ssl_certs)

        # Cleanup after exit (ctrl c)
        self.http_process.terminate()

    @app_http.route("/slowpage")
    async def slow_page(self):
        async def slow_response(response):
            response.write('<html><title>Slow Page</title><body><p>Slow Responses Start....</p>')
            for i in range(20):
                await asyncio.sleep(1)
                response.write('<p>SLOW</p>')
            response.write('<p><a href="/index.html">index</a></p></body></html>')
        return response.stream(slow_response, content_type='text/html')

    # This will timeout when the server hits its threshold.
    @app_http.route("/endlessBody")
    async def endless(self):
        async def endless(response):
            response.write('<html><title>Endless Body</title><body>\n')
            while True:
                await asyncio.sleep(1)
                response.write('<p><a href="/index.html>index</a></p>\n')
        return response.stream(endless, content_type='text/html')

    def generate_https_only_index(self):
        index_html = """
        <html>
            <title>Only Https Endpoint</title>
            <body>
                <p><a href="http://localhost:{}/index.html>HTTP INDEX</a></p>
            </body>
        </html>""".format(self.http_port)

        @self.app_https.route("/indexhttpsonly/")
        async def index_https_only(request):
            return response.html(index_html)

    def generate_index(self):
        index_html = """
        <html>
            <title>Bad Server Index</title>
            <body>
                <p><a href="/index.html">Circle Reference</a></p>"""
        for i in range(0, 10):
            index_html += """
                <p><a href="/endlessBody">endless %s</a></p>""" % i

        index_html += """
                <p><a href="/slowpage">Slow Page</a></p>
                <p><a href="/redirect_to_google">Sneaky redirect to external page</a></p>
                <p><a href="/bigcookie">Big Cookie</a></p>
                <p><a href="https://localhost:{https_port}/indexhttpsonly/">SSL Index</a></p>
                <p><a href="http://localhost:{http_port}/page1">Page1</a></p>
                <p><a href="/doesntexist.html">Doesn't exist link</a></p>
                <p><a href="/nonhtml.txt">Text Page</a></p>
                <p><a href="http://www.monzo.com/">Monzo.com</a></p>
            </body>
        </html>""".format(https_port=self.https_port, http_port=self.http_port)

        @self.app_http.route("index.html")
        @self.app_https.route("index.html")
        async def index(request):
            return response.html(index_html)

    @app_http.route("/redirect_to_google")
    async def redirect(self):
        return response.redirect(to="https://www.google.com/", status=302)

    @app_http.route("/")
    async def to_index(self):
        return response.redirect(to="/index.html", status=301)

    @app_http.route("/bigcookie")
    async def big_cookie(self):
        r = response.text("HUGE COOKIE")
        # cookies should be less than 4093 bytes in size.
        # should not have more than 50 cookies per domain
        # visiting this in say... chrome will give you:
        # The web page at http://localhost:8000/bigcookie might be temporarily down...
        # or it may have moved permanently to a new web address...
        # ERR_RESPONSE_HEADERS_TOO_BIG
        for i in range(1, 100):
            r.cookies["{}".format(i)] = "".join(("a" for i in range(0, 4096)))
        return r

    # Some Circular Routes
    @app_http.route("/page1")
    async def page1(self):
        return response.html('<html><body><p><a href="/page2">page2</a></p>')

    @app_http.route("/page2")
    async def page2(self):
        return response.html('<html><body><p><a href="/page3">page3</a></p>')

    @app_http.route("/page3")
    async def page3(self):
        return response.html('<html><body><p><a href="/page1">page1</a></p>')

    # A page that has a link in it bus isn't html
    @app_http.route("/nonhtml.txt")
    async def non_html(self):
        return response.text('An example of an http link would be <a href="/index.html">index</a>')


@click.command()
@click.option('--http-port', default=8000, help='port to run http server on (8000)')
@click.option('--https-port', default=8001, help='port to run https server on (8001)')
@click.option('--host', default="0.0.0.0", help='hosts to accept traffic from ("0.0.0.0")')
@click.option('--ssl-cert-location', default='certs/host.cert', help='SSL Cert location ("certs/host.cert")')
@click.option('--ssl-key-location', default='certs/host.key', help='SSL Key Location("certs/host.key")')
def run(http_port, https_port, host, ssl_cert_location, ssl_key_location):
    ssl = {"cert": ssl_cert_location, "key": ssl_key_location}
    server = BadServer(host=host, http_port=http_port, https_port=https_port, ssl_certs=ssl)
    server.run()


if __name__ == '__main__':
    run()