from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import PythonNews

def get_db():
    engine = create_engine('sqlite:///project_db.db')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

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

# function return dictionary of Heading and links
def extract_pyweekly_detail(bsoup):
    link_lst = []
    heading_lst = []
    paralst = []
    td = soup.find('td',class_='defaultText')
    anchor = td.find_all('a')[1:]

    # extract links
    for a in anchor:
        link_lst.append(a.get('href'))
    
    # extract heading
    for heading in anchor:
        heading_lst.append(heading.string)

    # extract paragraph
    for item in td.find_all('div'):
        if(item.find('span')):
            continue
        else:
            paralst.append(item.text)
    new_list = []
    for item in range(len(paralst)):
        new_list.append(paralst[item].strip())
    for item in new_list:
        if item=='':
            new_list.remove(item)
            
    return{
        'topic':heading_lst,
        'description':new_list,
        'link':link_lst
    }

if __name__ == '__main__':
    url = "https://www.pythonweekly.com/archive/23.html"
    soup = get_soup(url)
    data = []
    page_details = extract_pyweekly_detail(soup)
    time_format = datetime.datetime.now()
    df = pd.DataFrame(page_details)
    df['created_at'] = time_format
    # sess = get_db()
    engine = create_engine('sqlite:///project_db.db')
    df.to_sql(PythonNews.__tablename__,engine,if_exists='append',index=None)
    print("Successfully Saved to database")
    