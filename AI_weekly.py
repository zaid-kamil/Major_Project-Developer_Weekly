from bs4 import BeautifulSoup
import requests
import pandas as pd
import datetime
from sklearn import tree
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy import create_engine
from project_orm import AI_News

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

# function to find the category of the post
def find_category(class_name,bsoup):
    in_the_news_1 = bsoup.find('section',class_=''.join(class_name))
    category = in_the_news_1.find('span',class_='category__title__text')
    return category.string

def extract_sec_class_name(bsoup):
    # finding the div which contains all the section of the page
    div_body_of_page = bsoup.find('div',class_='issue__body')

    # finding all the sections from the div_body_of_page
    find_sections = div_body_of_page.find_all('section')

    # creating empty list to store the class name of the sections
    sec_class_lst = []

    # finding section which contains class, extracting the name of the section class and adding to the list
    for item in find_sections:
        if item.has_attr('class'):
    # sec_class_lst is created in format [['category','name_of_class']] that's why we are extracting index 1 of the list
            sec_class_lst.append(item['class'][1])

    # These are unwanted sections form the page that's why we are skipping them
    skip_clas_name_lst = ['cc-powered-by','cc-sponsor','cc-sponsorfooter','cc-footer']

    # removing the unwanted section class from the list, which sections we don't want
    for i in skip_clas_name_lst:
        sec_class_lst.remove(i)
    return sec_class_lst

# function to return the extracted data in the form of dictionary

def page_data(class_name_lst,bsoup):
    topic=[]
    link = []
    category = []
    para_info = []
    for class_name in class_name_lst:
        section_body = bsoup.find('section',class_=class_name)

        # extracting the achor text and link from each section
        div_in_sec = section_body.find_all('div',class_='item item--issue item--link')
        for div_body in div_in_sec:
            heading3_in_div = div_body.find('h3',class_='item__title')
            try:
                link_and_topic = heading3_in_div.find('a')
                topic.append(link_and_topic.string)
                link.append(link_and_topic.get('href'))

                # extracting paragraph from each section
                para_detail = div_body.find('p').text
                para_info.append(para_detail)

                # extracting category form each section
                category.append(find_category(class_name,bsoup))
            except Exception as e:
                print(e)
                continue
        # returning the dictionary of extracted data
    return {'category':category,
            'topic':topic,
            'description':para_info,
            'link':link
            }

# main function 
if __name__ == '__main__':
    url = 'https://aiweekly.co/'
    bsoup = get_soup(url)
    # calling function to return the list of classes present in the page
    page_class_list = extract_sec_class_name(bsoup)

    # calling function to extract all the details from the page
    final_data = page_data(page_class_list,bsoup)

    # finding the current date and time
    time_format = datetime.datetime.now()

    # creating dataframe of the extracted details
    df = pd.DataFrame(final_data)

    df['created_at'] = time_format
    engine = create_engine('sqlite:///project_db.db')
    df.to_sql(AI_News.__tablename__,engine,if_exists='replace',index=None)
    print("Successfully Saved to database")


