from sqlalchemy import create_engine
from sqlalchemy import Column,String,Integer,Float,DateTime,Boolean,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'Users'
    id = Column(Integer,primary_key=True)
    name = Column(String(50),nullable=False)
    email = Column(String(50),unique=True)
    password = Column(String(50))
    group = Column(Integer,default=1)
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self) -> str:
        return f'{self.id}|{self.name}|{self.group}'

class UserSelection(Base):
    __tablename__ = 'user_selections'
    id = Column(Integer,primary_key=True)
    has_python = Column(Boolean,default=False)
    has_cplusplus = Column(Boolean,default=False)
    has_ai = Column(Boolean,default=False)
    has_django = Column(Boolean,default=False)
    created_at = Column(DateTime,default=datetime.utcnow,nullable=False)
    user = Column(ForeignKey('Users.id'))

    def __repr__(self) -> str:
        return f'{self.id}'

class PythonNews(Base):
    __tablename__ = 'python_news'
    id = Column(Integer,primary_key=True)
    topic = Column(String(255))
    link = Column(String())
    description = Column(String())
    created_at =  Column(DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self) -> str:
        return f'{self.topic}'

class Cplusplus_News(Base):
    __tablename__ = 'cplusplus_news'
    id = Column(Integer,primary_key=True)
    category = Column(String(255))
    topic = Column(String())
    description = Column(String())
    link = Column(String())
    created_at =  Column(DateTime,default=datetime.utcnow,nullable=False)
    def __repr__(self) -> str:
        return f'{self.topic}'

class AI_News(Base):
    __tablename__ = 'ai_news'
    id = Column(Integer,primary_key=True)
    category = Column(String(255))
    topic = Column(String())
    description = Column(String())
    link = Column(String())
    created_at =  Column(DateTime,default=datetime.utcnow,nullable=False)

class Java_News(Base):
    __tablename__ = 'java_news'
    id = Column(Integer,primary_key=True)
    source = Column(String(255))
    topic = Column(String())
    link = Column(String())
    created_at =  Column(DateTime,default=datetime.utcnow,nullable=False)

class Django_News(Base):
    __tablename__ = 'django_news'
    id = Column(Integer,primary_key=True)
    category = Column(String(255))
    topic = Column(String())
    description = Column(String())
    link = Column(String())
    created_at =  Column(DateTime,default=datetime.utcnow,nullable=False)

    def __repr__(self) -> str:
        return f'{self.topic}'




if __name__ == "__main__":
    engine = create_engine('sqlite:///project_db.db')
    Base.metadata.create_all(engine)