from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from base import config_str, make_repr

Base = declarative_base()
engine = create_engine(config_str, echo=True)
md = MetaData(engine)

class Student(Base):
    __table__ = Table("student", md, autoload=True)

    def __repr__(self):
        return make_repr(
            self, ["s_id", "s_name", "s_birth", "s_sex"], one_row=False)

class Course(Base):
    __table__ = Table("course", md, autoload=True)

    def __repr__(self):
        return make_repr(self, ["c_id", "c_name", "t_id"])

class Teacher(Base):
    __table__ = Table("teacher", md, autoload=True)

    def __repr__(self):
        return make_repr(self, ["t_id", "t_name"])

class SC(Base):
    __table__ = Table("sc", md, autoload=True)

    def __repr__(self):
        return make_repr(self, ["s_id", "c_id", "score"])


if __name__ == "__main__":

    get_session = sessionmaker(engine)

    session = get_session()
    print(session.query(Student).first())
