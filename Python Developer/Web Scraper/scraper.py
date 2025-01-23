import os
import requests
import string

from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, page_count: int, article_type: str):
        """
        WebScraper class to scrape articles from nature.com.

        :param page_count: int - number of pages to scrape
        :param article_type: str - type of article to scrape
        """
        # Force english headers
        self.headers = {'Accept-Language': 'en-US,en;q=0.5'}
        # Base url provided by Hyperskill
        self.base_url = 'https://www.nature.com/nature/articles?sort=PubDate&year=2020&page='
        self.page_count = page_count
        self.article_type = article_type
        for i in range(1, self.page_count + 1):
            # Make a call to get a page of articles from nature.com
            self.initial_request = requests.get(f"{self.base_url}{i}", headers=self.headers)
            if self.initial_request.status_code == 200:
                self.initial_soup = (BeautifulSoup(self.initial_request.content, 'html.parser')
                                     .find_all('article'))
                # Create any missing directories
                if os.path.exists(f"./Page_{i}"):
                    pass
                else:
                    os.mkdir(f"./Page_{i}")
                # Iterate through each article located on a page.
                for article in self.initial_soup:
                    # Only keep the ones with a correct type.
                    if article.find('span', attrs={'data-test': 'article.type'}).text == self.article_type:
                        # Take the article title, strip trailing spaces, remove punctuation, then replace all spaces
                        # with underscores.
                        article_title = (article.find('a', attrs={'data-track-action': 'view article'})
                                         .text
                                         .rstrip()
                                         .translate(str.maketrans('', '', string.punctuation))
                                         .translate(str.maketrans(' ', '_')))
                        # Get the link to the article and create an absolute url.
                        article_contents_link = article.find('a', attrs={'data-track-action': 'view article'}).get('href')
                        article_contents_link = "https://www.nature.com/nature" + article_contents_link
                        # Make a request to the article itself and parse.
                        request = requests.get(article_contents_link, headers=self.headers)
                        beautiful_soup = BeautifulSoup(request.content, 'html.parser')
                        # Grab the article body. Since we're paywalled, we're just grabbing the teaser.
                        article_body = beautiful_soup.find('p', attrs={'class': 'article__teaser'}).text
                        with open(f'./Page_{i}/{article_title}.txt', 'w', encoding='utf-8') as outfile:
                            outfile.write(article_body)
                        print(f'{article_title}.txt saved')
            else:
                print('Invalid resource!')
                break
        print('Saved all articles')


if __name__ == '__main__':
    pages = int(input())
    article_type = input()
    WebScraper(page_count=pages,
               article_type=article_type)