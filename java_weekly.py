from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine

def get_soup(url):
    try:
        page = requests.get(url)
        if page.status_code == 200:
            soup = BeautifulSoup(page.text,'html.parser')
            return soup
        else:
            print("page error",page.status_code)
            return None
    except:
        print("Internet error")
        return None

def get_news_soup(url = 'https://java.libhunt.com/newsletter'):
    home_page = get_soup(url)
    news = home_page.find('div',attrs={'class':'text-center text-strong-invite'}).a.attrs.get('href')
    newsletter_url = "https://java.libhunt.com"+news
    print(newsletter_url)
    news_soup = get_soup(newsletter_url)
    return news_soup

def extract_news(news_soup):
    news_ul = news_soup.find('ul',attrs={'class':'newsletter-stories'})
    if news_ul is None:
        print("No news")
        return None
    else:
        news_list = []
        for li in news_ul.find_all('li',attrs={'class':'story'}):
            news_dict = {}
            news_dict['topic'] = li.find('a',attrs={'class':'title'}).text
            news_dict['link'] = li.find('a',attrs={'class':'title'}).attrs.get('href')
            news_dict['source'] = li.find('div',attrs={'class':'host'}).text
            news_list.append(news_dict)
        return news_list

if __name__ == '__main__':
    news_soup = get_news_soup()
    news_list = extract_news(news_soup)
    print(news_list)