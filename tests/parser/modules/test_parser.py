import pytest
from asyncio import Queue
from aiohttp import web
from aiohttp import ClientSession

from parser.modules import Parser

pytestmark = pytest.mark.asyncio

HTML_TEMPLATE: str = "<html><body>%s</body></html>"
TITLE_TEMPLATE: str = "<title>%s</title>"
LINK_TEMPLATE: str = "<a href='%s'>Link text</a>"


@pytest.fixture
def queue() -> Queue:
    return Queue()


def make_html(links_count: int, page_title: str, parent_page: str = "") -> str:
    links: str = ''.join([LINK_TEMPLATE % (parent_page + str(i)) for i in range(links_count)])
    title: str = TITLE_TEMPLATE % parent_page + page_title
    html: str = HTML_TEMPLATE % (title + links)
    return html


async def get_empty_page(_):
    return web.Response(body="")


async def get_start_page(_):
    return web.Response(body=make_html(links_count=0, page_title="start page"))


@pytest.fixture
def cli(loop, aiohttp_client):
    app = web.Application()
    app.router.add_get('https://test.url', get_empty_page)
    app.router.add_get('https://test.url/40', get_empty_page)
    return loop.run_until_complete(aiohttp_client(app))


def test_get_links_parser(queue: Queue) -> None:
    start_url: str = "https://test.url/40"
    start_page_html: str = make_html(links_count=0, page_title="start page")

    parser: Parser = Parser(queue=queue, start_url=start_url)
    links: set = parser._get_links(url=start_url, html=start_page_html)
    assert len(links) == 0

    links_count: int = 5
    child_page_html: str = make_html(
        links_count=links_count,
        page_title="Child page",
        parent_page=start_url,
    )
    links = parser._get_links(url=start_url, html=child_page_html)
    assert len(links) == links_count
    with pytest.raises(AssertionError):
        assert links == ""
    for i in range(5):
        assert start_url + str(i) in links


async def test_check_site_avail(queue: Queue) -> None:
    available_url: str = "https://test.url"
    parser: Parser = Parser(queue=queue, start_url=available_url)
    async with ClientSession() as session:
        check_result: bool = await parser.check_site_avail(session=session)
        assert check_result == True

    not_available_url: str = "https://test.url/999"
    parser: Parser = Parser(queue=queue, start_url=not_available_url)
    async with ClientSession() as session:
        check_result: bool = await parser.check_site_avail(session=session)
        assert check_result == False
