# Badserver

A HTTP(s) server which simulates a website. Useful for http client and scraper testing. It does a few quite naughty things.

* Serves endless pages which will send you a line of html every second **forever**
* Serves a page containing absurdly large cookies (and far too many of them)
* Pretends to have a local relative link that really does a 302 redirect to google

## Quickstart

If you just want to run it it's hosted on dockerhub

```
docker run -p 8000:8000 -p 8001:8001 transactcharlie/badserver
```

## One Million Links
if you request `/one_million_links` badserver will stream you a million links that resolve to a valid dynamic path `/random/<int>`. Hitting this endpoint is a good way to test your client can cope with a *lot* of valid data and streaming endpoints.

`/one_million_links` is not linked to by `index.html` so that crawlers don't have to deal with this unless they want to.

## Sitemap for Crawlers Targeting (`/`)
If you write a crawler it should returns results similar to this if you target the root (`/`) or `/index.html`:

![Sitemap](docs/sitemap.png)

(Sitemap generated by [scraping-spider](https://github.com/TransactCharlie/scraping-spider))
