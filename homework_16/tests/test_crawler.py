# pip install pytest-asyncio
import pytest
#from bs4 import BeautifulSoup
from ..crawler import fetch, parse_news, parse_comments, save_to_disk
import aiohttp
#import asyncio
import os
import json
from datetime import datetime


@pytest.mark.asyncio
async def test_fetch():
    async with aiohttp.ClientSession() as session:
        url = "https://news.ycombinator.com/"
        html = await fetch(session, url)
        assert isinstance(html, str)
        assert len(html) > 0


def test_parse_news():
    html = """
    <tr class="athing">
        <td class="titleline"><a href="https://example.com">Example Title</a></td>
    </tr>
    <tr>
        <td class="subtext"><span class="score">10 points</span>
        <a href="item?id=12345">10 comments</a></td>
    </tr>
    """
    articles = parse_news(html)
    assert len(articles) == 1
    assert articles[0]['title'] == "Example Title"
    assert articles[0]['url'] == "https://example.com"
    assert articles[0]['score'] == "10 points"
    assert articles[0]['comments_link'] == "item?id=12345"


def test_parse_comments():
    html = """
    <div class="comment">
        <div class="commtext"><a href="https://example.com/comment1">Comment 1</a></div>
    </div>
    <div class="comment">
        <div class="commtext"><a href="https://example.com/comment2">Comment 2</a></div>
    </div>
    """
    comment_urls = parse_comments(html)
    assert len(comment_urls) == 2
    assert "https://example.com/comment1" in comment_urls
    assert "https://example.com/comment2" in comment_urls


@pytest.mark.asyncio
async def test_save_to_disk():
    articles = [
        {
            'title': 'Example Title',
            'url': 'https://example.com',
            'score': '10 points',
            'comments_link': 'item?id=12345',
            'comment_urls': []
        }
    ]
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'news_{timestamp}.json'
    await save_to_disk(articles)

    # Check if file is created
    assert os.path.exists(filename)

    # Load file and check its contents
    with open(filename, 'r') as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]['title'] == 'Example Title'
        assert data[0]['url'] == 'https://example.com'
        assert data[0]['score'] == '10 points'
        assert data[0]['comments_link'] == 'item?id=12345'
        assert data[0]['comment_urls'] == []

    # Clean up file after the test
    os.remove(filename)


if __name__ == "__main__":
    pytest.main()
