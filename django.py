from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import Django_News

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

# extracting category of the article
def article_category(soup,class_name):
    article = soup.find('section',class_=class_name)
    category = article.find('h2').find('span')
    return category.string
    
# finding names of the class present in section
def preprocessing_data(soup):
    cls_name = []
    remove_item = ['cc-news','cc-trendsandinsights','cc-events','cc-sponsored-link-bottom','cc-sponsored-link-top','cc-sponsorship']
    issue = soup.find('div',class_='issue__body')
    body = issue.find_all('section')
    for item in body:
        if item.has_attr('class'):
            cls_name.append(item['class'])

    for item1 in remove_item:
        for item in cls_name:
            if item1==item[1]:
                cls_name.remove(item)
    return cls_name

def extract_details(soup,class_name):
    category =[]
    topic = []
    description = []
    link = []
    for name in class_name:
        try:
            section = soup.find('section',class_=name[1])
            div_in_sec = section.find_all('div',class_='item item--issue item--link')
            for item in div_in_sec:
                category.append(article_category(soup,name[1]))
                content = item.find('h3',class_='item__title')
                topic.append(content.find('a').string)
                description.append(item.find('p').string)
                link.append(content.find('a').get('href'))
        except Exception as e:
            print(e)
            continue
    return{
        'category':category,
        'topic':topic,
        'description':description,
        'link':link
    }

if __name__ == '__main__':
    url = 'https://django-news.com/'
    soup = get_soup(url)
    time_format = datetime.datetime.now()
    name_of_classes = preprocessing_data(soup)
    details = extract_details(soup,name_of_classes)
    df = pd.DataFrame(details)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project_db.db')
    df.to_sql(Django_News.__tablename__,engine,if_exists='replace',index=None)
    print("Successfully Saved to database")