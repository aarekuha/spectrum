import pytest
from asyncio import Queue
from aiohttp import ClientSession
from pytest_mock import MockerFixture

from parser.modules import Parser

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


def test_get_links_parser_empty(queue: Queue) -> None:
    start_url: str = "https://test.url/40"
    start_page_html: str = make_html(links_count=0, page_title="start page")

    status_store: dict = {}
    parser: Parser = Parser(queue=queue, start_url=start_url, status_store=status_store)
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

def test_get_links_parser_containing(queue: Queue) -> None:
    start_url: str = "https://test.url/40"
    status_store: dict = {}
    parser: Parser = Parser(queue=queue, start_url=start_url, status_store=status_store)

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

class MockResponse:
    def __init__(self, status):
        self.status = status

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


@pytest.mark.asyncio
async def test_check_site_avail_ok(queue: Queue, mocker: MockerFixture) -> None:
    status_store: dict = {}
    parser: Parser = Parser(queue=queue, start_url="", status_store=status_store)
    session: ClientSession = ClientSession()

    mocker.patch('aiohttp.ClientSession.get', return_value=MockResponse(status=200))
    assert await parser.check_site_avail(session=session) == True

    await session.close()


@pytest.mark.asyncio
async def test_check_site_avail_failed(queue: Queue, mocker: MockerFixture) -> None:
    status_store: dict = {}
    parser: Parser = Parser(queue=queue, start_url="", status_store=status_store)
    session: ClientSession = ClientSession()

    mocker.patch('aiohttp.ClientSession.get', return_value=MockResponse(status=404))
    assert await parser.check_site_avail(session=session) == False

    await session.close()
