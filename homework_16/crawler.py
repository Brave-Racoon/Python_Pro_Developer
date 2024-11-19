import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import json

BASE_URL = "https://news.ycombinator.com/"


async def fetch(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch {url}: {response.status}")
        return await response.text()


def parse_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    for item in soup.select('.athing'):
        title_elem = item.select_one('.titleline a')
        score_elem = item.find_next_sibling('tr').select_one('.score')
        comments_link_elem = item.find_next_sibling('tr').select_one('.subtext a[href*="item?id="]')

        title = title_elem.text
        url = title_elem['href']
        score = score_elem.text if score_elem else "0 points"
        comments_link = comments_link_elem['href'] if comments_link_elem else ""

        articles.append({
            'title': title,
            'url': url,
            'score': score,
            'comments_link': comments_link,
            'comment_urls': []  # Placeholder for comment URLs
        })

    return articles


def parse_comments(html):
    soup = BeautifulSoup(html, 'html.parser')
    comment_urls = []

    for comment in soup.select('.comment .commtext a'):
        comment_url = comment['href']
        comment_urls.append(comment_url)

    return comment_urls


async def save_to_disk(articles):
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    filename = f'news_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(articles, f, indent=4)  # Prettify JSON
        print(f'Saved articles to {filename}')


async def crawl():
    async with aiohttp.ClientSession() as session:
        while True:
            html = await fetch(session, BASE_URL)
            articles = parse_news(html)

            # Check if articles list is populated
            if not articles:
                print("No articles found in the HTML.")

            # Fetch and parse comments for each article
            for article in articles:
                if article['comments_link']:
                    comments_html = await fetch(session, f"https://news.ycombinator.com/{article['comments_link']}")
                    article['comment_urls'] = parse_comments(comments_html)

            await save_to_disk(articles)
            await asyncio.sleep(20)


if __name__ == "__main__":
    print("Crawler started.")
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(crawl())
    except KeyboardInterrupt:
        print("Crawler stopped.")
