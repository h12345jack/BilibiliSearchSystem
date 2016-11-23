#coding=utf8


from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from settings import MYSQL_CONFIG

Base = declarative_base()




def db_connect():
    return create_engine(
            "mysql://"+MYSQL_CONFIG["USERNAME"]+\
            ":"+MYSQL_CONFIG["PASSWORD"]+\
            "@"+MYSQL_CONFIG["HOST"]+\
            "/"+MYSQL_CONFIG["DBNAME"]+"?charset=utf8")


def create_video_info_table(engine):
    Base.metadata.create_all(engine)

class Videos(Base):
    __tablename__ = 'video_info'
    mysql_engine = 'MyISAM'
    k_id         = Column(String(20),primary_key=True)
    url          = Column(String(250), unique=True)
    crawl_time   = Column(Integer)
    title        = Column(String(1000))
    keywords     = Column(String(1000))
    description  = Column(String(1000))
    author       = Column(String(1000))
    cover_image  = Column(String(1000))
    h_title      = Column(String(1000))
    startDate    = Column(String(1000))
    cid          = Column(Integer)
    aid          = Column(Integer)
    info         = Column(String(2000))
    upinfo       = Column(String(2000))
    video_info   = Column(String(2000))
    tag_list    = Column(String(2000))
    stats       = Column(Text)
    
    