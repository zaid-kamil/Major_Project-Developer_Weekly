from smtpd import SMTPServer
from sqlalchemy import create_engine, engine_from_config, false, true
from project_orm import Cplusplus_News, Java_News, User,UserSelection,PythonNews,AI_News,Django_News
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from flask.globals import request
from flask import Flask,render_template,flash,redirect, request, session,url_for
from utils import *
import pandas as pd
import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from cpp_newsletter import *
from AI_weekly import *
from django import *
from java_weekly import *

app = Flask(__name__)
app.secret_key = 'the basics of life with python'


def get_db():
    engine = create_engine('sqlite:///project.sqlite')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

# for index
@app.route('/',methods=['GET','POST'])
def index():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)
        print(password)
        if email and validate_email(email):
            if password and len(password)>=6:
                try:
                    sess = get_db()
                    user_profile = sess.query(User).filter_by(email=email,password=password).first()
                    if user_profile:
                        session['isauth'] = True
                        session['email'] = user_profile.email
                        session['id'] = user_profile.id
                        session['name'] = user_profile.name
                        sess.close()
                        flash('Login Successful','success')
                        return redirect('/home')
                    else:
                        flash("Please enter the correct fields",'danger')
                except Exception as e:
                    flash(e,'danger')
    if session.get('isauth'):
        return redirect('/home')
    return render_template('index.html',title='Login')

# for signup
@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name)>=3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            sess.close()
                            flash("Registration Successfull",'success')
                            return redirect('/')
                        except Exception as e:
                            print(e)
                            flash("Account already exist",'warning')
                    else:
                        flash('Confirm password does not match')
                else:
                    flash('Password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('Invalid name, must be 3 or more characters','danger')
    return render_template('signup.html',title='Register')

# for home
@app.route('/home',methods=['GET','POST'])
def home():

    if session.get('isauth',False):
        sess = get_db()
        results = sess.query(UserSelection).filter(UserSelection.user==session.get('id')).first()
        # print(results)
        if results:
            sess.close()
            flash('your saved preferences have been found in database','info')
            return redirect('/dashboard')
        else:
            flash('You have to login first','warning')
            sess.close()
        checked_java=checked_python=checked_cpluslus=checked_ai=checked_django=False
        if request.method=="POST":
            if request.form.get('python','off')=='on':
                checked_python=True
            if request.form.get('cplusplus','off')=='on':
                checked_cpluslus = True
            if request.form.get('ai','off')=='on':
                checked_ai = True
            if request.form.get('django','off')=='on':
                checked_django = True
            if request.form.get('java','off')=='on':
                checked_java = True
            

            if (checked_java or checked_python or checked_cpluslus or checked_ai or checked_django)==False:
                flash('You did not selected any of the options','warning')
            else:
                sess = get_db()
                news_data = UserSelection(has_python=checked_python,has_cplusplus=checked_cpluslus,has_ai=checked_ai,has_django=checked_django,has_java=checked_java,user=session.get('id'))
                sess.add(news_data)
                sess.commit()
                sess.close()
                flash('Successfully saved you selection','success')
                return redirect('/dashboard')
        return render_template('home.html',title='Home')
    else:
        return redirect('/')

@app.route('/change',methods=['GET','POST'])
def change_pref():
    ctx={}
    if session.get('isauth',False):
        sess = get_db()
        results = sess.query(UserSelection).filter(UserSelection.user==session.get('id')).first()
        # print(results)
        if results:
            flash('your saved preferences have been found in database','info')
            ctx['results'] = results
        else:
            flash('You have to login first','warning')
        checked_java = checked_python=checked_cpluslus=checked_ai=checked_django=False
        if request.method=="POST":
            if request.form.get('python','off')=='on':
                checked_python=True
                results.has_python=True
            if request.form.get('cplusplus','off')=='on':
                checked_cpluslus = True
                results.has_cplusplus=True
            if request.form.get('ai','off')=='on':
                checked_ai = True
                results.has_ai=True
            if request.form.get('django','off')=='on':
                checked_django = True
                results.has_django=True
            if request.form.get('java','off')=='on':
                checked_java = True
                results.has_java=True

            if (checked_python or checked_cpluslus or checked_ai or checked_django or checked_java)==False:
                flash('You did not selected any of the options','warning')
            else:
                print(results)
                sess.query(UserSelection).update({'has_python':checked_python,'has_cplusplus':checked_cpluslus,'has_ai':checked_ai,'has_django':checked_django,'has_java':checked_java})
                sess.commit()
                sess.close()
                flash('Successfully updated your selections','success')
                return redirect('/dashboard')
        else:
            sess.close()
    return render_template('change_prefs.html',title='Home',data=ctx)
    
# for about
@app.route('/about')
def about():
    return render_template('about.html',title='About')


# for dashboard 
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if session.get('isauth',False):
        sess = get_db()

        results = sess.query(UserSelection).filter(UserSelection.user==session.get('id')).first()
        if results:
            
            pdata=cppdata=aidata=djangodata=javadata=None
            print(results.has_python)
            if results.has_python:
                pdata = sess.query(PythonNews).all()
            if results.has_cplusplus:
                cppdata = sess.query(Cplusplus_News).all()
            if results.has_ai:
                aidata = sess.query(AI_News).all()
            if results.has_django:
                djangodata = sess.query(Django_News).all()
            if results.has_java:
                javadata = sess.query(Java_News).all()
            sess.close()

            return render_template('dashboard.html',title='News_Dashboard',
                    python_news = pdata,
                    cpp_news = cppdata,
                    ai_news=aidata,
                    django_news = djangodata,
                    java_news=javadata)
        else:
            return redirect('/home')
    else:
        return redirect('/')


# for news on single technology when clicked
@app.route('/detail')
def details():
    sess = get_db()
    selection = request.args.get('f')
    if selection=='p':
        data = sess.query(PythonNews).all()
    if selection=='c':
        data = sess.query(Cplusplus_News).all()
        print(data)
    if selection=='a':
        data = sess.query(AI_News).all()
    if selection=='d':
        data = sess.query(Django_News).all()
    if selection=='j':
        data = sess.query(Java_News).all()

    return render_template('detail.html',title='News_Dashboard',selected=selection,details=data)


# for logout
@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/')

# for forgot
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    sess = get_db()
    if request.method=="POST":
        mail = request.form.get('email')
        print(mail)
        res = sess.query(User).filter(User.email==mail).first()
        pwd = res.password
        mail_content = pwd
        sender_email = 'dev.weekly2022@gmail.com'
        password = 'dev5404Weekly'
        receiver_email = mail
        message = ''.join(pwd)
        smtp_server = "smtp.gmail.com"
        port = 587

        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(smtp_server,port)
            server.ehlo() # Can be omitted
            server.starttls(context=context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(sender_email, password)
            # TODO: Send email here
            server.sendmail(sender_email,receiver_email,message)
            print("Mail sended")
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()
    return render_template('forgot.html',title='Forgot password')

def update_cpp():
    start_url = "https://cpp.libhunt.com/newsletter"
    page = requests.get(start_url).text
    soup = BeautifulSoup(page,'html.parser')
    url = "https://cpp.libhunt.com"+soup.find('div',attrs={'class':'text-center text-strong-invite'}).a.attrs.get('href')
    bsoup = get_soup(url)

    # calling function to extract the details from the page
    final_data = extract_newsletter(bsoup)

    # finding the current date and time
    time_format = datetime.datetime.now()

    # creating dataframe of the extracted details
    df = pd.DataFrame(final_data)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(Cplusplus_News.__tablename__,engine,if_exists='replace',index=True,index_label='id')
    print("Successfully Saved to database")

def update_ai():
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
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(AI_News.__tablename__,engine,if_exists='replace',index=True,index_label='id')
    print("Successfully Saved to database")

def update_django():
    url = 'https://django-news.com/'
    soup = get_soup(url)
    time_format = datetime.datetime.now()
    name_of_classes = preprocessing_data(soup)
    details = extract_details(soup,name_of_classes)
    df = pd.DataFrame(details)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(Django_News.__tablename__,engine,if_exists='replace',index=True,index_label='id')
    print("Successfully updated django weekly")


def update_java():
    news_soup = get_news_soup()
    news_list = extract_news(news_soup)
    time_format = datetime.datetime.now()
    df = pd.DataFrame(news_list)
    df['created_at'] = time_format
    engine = create_engine('sqlite:///project.sqlite')
    df.to_sql(Java_News.__tablename__,engine,if_exists='replace',index=True,index_label='id')
    print("Successfully updated java weekly")
    

if __name__ == '__main__':
    update_cpp()
    update_ai()
    update_django()
    update_java()
    app.run(debug=True)