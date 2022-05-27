
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import Js_News

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

def js_extract_data(soup):
    data = []
    rows = soup.find_all('table',class_='el-item item')
    for row in rows:
        title = row.find('span',class_='mainlink').a.text
        link = row.find('span',class_='mainlink').a.attrs.get('href')
        description = row.find('p',class_='desc').text
        source = row.find('p',class_='name').text
        data.append({
            'topic':title,
            'link':link,
            'description':description,
            'source':source,
        })
    return data

if __name__ == "__main__":
    jssoup = get_soup('https://javascriptweekly.com/')
    atags = jssoup.find('div',attrs={'class':'main'}).find_all('a')
    issue_path = atags[2].attrs.get('href')
    soup = get_soup('https://javascriptweekly.com/'+issue_path)
    data = js_extract_data(soup)
    time_format = datetime.datetime.now()
    df = pd.DataFrame(data)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(Js_News.__tablename__,engine,if_exists='replace',index=True,index_label='id')
    print("Successfully Saved to database")