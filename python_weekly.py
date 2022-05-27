from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import PythonNews

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

def py_extract_details(soup):
    data = []
    target = soup.find_all('ul',class_='newsletter-stories')
    for ultag in target:
        for item in ultag.find_all('li'):
            try:
                linktag = item.find('a',attrs={'class':'title'})
                title = linktag.text
                link = linktag.get('href')
                source = item.find('div',class_='host').text
                data.append({
                    'topic':title,
                    'link':link,
                    'source':source,
                })   
            except:
                pass
    return data

if __name__ == '__main__':
    url ='https://python.libhunt.com/newsletter/312'
    soup = get_soup(url)
    time_format = datetime.datetime.now()
    details = py_extract_details(soup)
    df = pd.DataFrame(details)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(PythonNews.__tablename__,engine,if_exists='replace',index=None)
