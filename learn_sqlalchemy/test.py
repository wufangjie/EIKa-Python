import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Query
# from sqlalchemy import Column, Integer, String, Date, SmallInteger
from sqlalchemy import exists, and_, or_, not_, distinct, desc, tuple_
from sqlalchemy import func, over, text#, funcfilter

from pprint import pprint
from db_model import Student, Course, Teacher, SC
from base import config_str

# engine = create_engine('sqlite:///:memory:', echo=True)
session = sessionmaker(create_engine(config_str, echo=True))() # for test



if __name__ == "__main__":
    engine = create_engine(config_str, echo=True)#False)
    get_session = sessionmaker(engine)
    with get_session() as session:
        pass
        #p42_4(session)
