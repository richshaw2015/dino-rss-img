
import re
from urllib.parse import urlparse, urljoin
from scrapy.http import HtmlResponse
import logging
import urllib.request
import requests
import os

SERVER = 'http://localhost:8000'


def get_short_host_name(url: str) -> str:
    return re.sub(r'^www\.|^blog\.|^blogs\.|^tech\.', '', urlparse(url).netloc)


def get_html(url: str) -> str:
    host = get_short_host_name(url)
    html_file = os.path.join('cache', f"{host}.html")

    if os.path.exists(html_file):
        return open(html_file, encoding='UTF8').read()
    else:
        try:
            rsp = requests.get(url, timeout=30, verify=False)
            if rsp and rsp.ok:
                open(html_file, 'w', encoding='UTF8').write(rsp.text)
                return rsp.text
        except Exception as e:
            logging.warning(f"{url}: {e}")

    return ''


def sync_host_favicon(url: str) -> str:
    host = get_short_host_name(url)
    png = os.path.join('png', f"{host}.png")
    jpg = os.path.join('png', f"{host}.jpg")

    if os.path.exists(png):
        return png
    elif os.path.exists(jpg):
        return jpg
    else:
        icon, html = '', get_html(url)

        if html:
            response = HtmlResponse(url=host, body=html, encoding='utf8')

            icon = response.selector.xpath("//link[@rel='apple-touch-icon'][last()]/@href").extract_first()
            if not icon:
                icon = response.selector.xpath("//link[@rel='apple-touch-icon-precomposed'][last()]/@href").\
                    extract_first()
            if not icon:
                icon = response.selector.xpath("//meta[@name='twitter:image']/@content").extract_first()
            if not icon:
                icon = response.selector.xpath("//meta[@name='og:image']/@content").extract_first()
            if not icon:
                icon = response.selector.xpath("//link[@rel='icon'][last()]/@href").extract_first()

            if icon:
                icon_url = urljoin(url, icon.strip())
                try:
                    urllib.request.urlretrieve(icon_url, png)
                except Exception as e:
                    logging.warning(f"{icon_url}: {e}")
            else:
                logging.warning(url)

        return icon


def main() -> None:
    rsp = requests.get(f"{SERVER}/api/monitor/todo/feeds")
    links = rsp.json()['links']

    for link in links:
        sync_host_favicon(link)


if __name__ == '__main__':
    main()
