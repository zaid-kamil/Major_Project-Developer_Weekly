from time import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import Cplusplus_News


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

def extract_newsletter(bsoup):
    final_link = []
    link = []
    topic = []
    category = []
    library_project_desc = []

    # finding ul from the page
    ul_news_article = bsoup.find('ul',class_='newsletter-stories no-bullet')

    # finding all the div tags from the ul
    all_div_news_article = ul_news_article.find_all('div',class_='column')

    # finding all the anchor tags and extractng the link and string from the anchor tag
    for achr in all_div_news_article:
        try:
            if achr.find('a',class_='thumb-wrapper'):
                
                link.append(achr.find('a',class_='thumb-wrapper').get('href'))
                topic.append(achr.find('a',class_='thumb-wrapper').string)
            if achr.find('a',class_='title'):
                
                link.append(achr.find('a',class_='title').get('href'))
                topic.append(achr.find('a',class_='title').string)
        except Exception as e:
            print(e)
            continue

    # removing duplicate links from the link list and adding to the new list "final_link"
    for item in range(0,len(link),2):
        final_link.append(link[item])
        category.append('Popular News and Articles')

    # removing the None elements form the list
    for item in topic:
        if item == None:
            topic.remove(item)


    # extracting links from Trending libraries and projects
    ul_library_project = bsoup.find('ul',class_='newsletter-projects no-bullet')
    lib_a = ul_library_project.find_all('a',class_='title')
    for item in lib_a:
        final_link.append(item.get('href'))
        topic.append(item.string)

    # extracting description or paragraph from the Trending libraries and projects
    ul_library_project = bsoup.find('ul',class_='newsletter-projects no-bullet')
    descrip = ul_library_project.find_all('p',class_='description')

    # purpose of this loop is only to make the same size of array by filling NA values
    for item in range(0,12):
        library_project_desc.append("Description is not available")

    # extracting description from Trending libraries and project section
    for item in descrip:
        category.append('Trending libraries and projects')
        library_project_desc.append(item.string.strip())

    # extracting release date of newsletter
    file_date = bsoup.find('div',class_='column shrink')
    release_date = file_date.find('strong',text='Release Date').next_sibling.next_sibling.strip()

    # removing space and ',' from the release_date
    for item in range(len(release_date)):
        if release_date[item]==' ':
            r_date = release_date.replace(' ','_')
        if release_date[item]==',':
            newsletter_date = r_date.replace(',','_')
    return {"Category":category,
            "Topic":topic,
            "Description":library_project_desc,
            "Link": final_link #first converting the link list into set for unique ele and then set to list bcause list is ordere
            }

if __name__ == '__main__':
    url = 'https://cpp.libhunt.com/newsletter/296'
    bsoup = get_soup(url)

    # calling function to extract the details from the page
    final_data = extract_newsletter(bsoup)

    # finding the current date and time
    time_format = datetime.datetime.now()

    # creating dataframe of the extracted details
    df = pd.DataFrame(final_data)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project_db.db')
    df.to_sql(Cplusplus_News.__tablename__,engine,if_exists='append',index=None)
    print("Successfully Saved to database")
