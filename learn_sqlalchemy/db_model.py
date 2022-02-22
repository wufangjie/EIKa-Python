from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, SmallInteger, DECIMAL
from base import make_repr
from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Base = declarative_base() # declarative base class

@as_declarative()
class Base:
    # id: Any # for Base crud method
    __name__: str # for __tablename__ classmethod
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()



class Student(Base):
    #__tablename__ = 'student'

    s_id = Column(Integer, primary_key=True, autoincrement=True)
    s_name = Column(String(10), nullable=False, comment="姓名")
    s_birth = Column(Date, comment="生日")
    s_sex = Column(String(1), default="男") # actually char(1)

    def __repr__(self):
        return make_repr(
            self, ["s_id", "s_name", "s_birth", "s_sex"], one_row=False)

class Course(Base):
    #__tablename__ = 'course'

    c_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    c_name = Column(String(10))
    t_id = Column(Integer) # actually char(1)

    def __repr__(self):
        return make_repr(self, ["c_id", "c_name", "t_id"])

class Teacher(Base):
    #__tablename__ = 'teacher'

    t_id = Column(Integer, primary_key=True, autoincrement=True)
    t_name = Column(String(10))

    def __repr__(self):
        return make_repr(self, ["t_id", "t_name"])

class SC(Base):
    #__tablename__ = 'sc'

    s_id = Column(Integer, primary_key=True)
    c_id = Column(SmallInteger, primary_key=True)
    score = Column(DECIMAL(4, 1))

    def __repr__(self):
        return make_repr(self, ["s_id", "c_id", "score"])

def make_record(col_name, row_list):
    return [dict(zip(col_name, lst)) for lst in row_list]

if __name__ == "__main__":
    student_col = ["s_name", "s_birth", "s_sex"]
    student_lst = [Student(**dict(zip(student_col, lst))) for lst in [
        ('赵雷', '1990-01-01', '男'),
        ('钱电', '1990-12-21', '男'),
        ('孙风', '1990-05-20', '男'),
        ('李云', '1990-08-06', '男'),
        ('周梅', '1991-12-01', '女'),
        ('吴兰', '1992-03-01', '女'),
        ('郑竹', '1989-07-01', '女'),
        ('王菊', '1990-01-20', '女')]];

    course_col = ["c_name", "t_id"]
    course_lst = [Course(**dict(zip(course_col, lst))) for lst in [
        ('语文', 2),
        ('数学', 1),
        ('英语', 3)]];

    teacher_col = ["t_name"]
    teacher_lst = [Teacher(**dict(zip(teacher_col, lst))) for lst in [
        ('张三',),
        ('李四',),
        ('王五',)]];

    sc_col = ["s_id", "c_id", "score"]
    sc_lst = [SC(**dict(zip(sc_col, lst))) for lst in [
        (1, 1, 80),
        (1, 2, 90),
        (1, 3, 99),
        (2, 1, 70),
        (2, 2, 60),
        (2, 3, 80),
        (3, 1, 80),
        (3, 2, 80),
        (3, 3, 80),
        (4, 1, 50),
        (4, 2, 30),
        (4, 3, 20),
        (5, 1, 76),
        (5, 2, 87),
        (6, 1, 31),
        (6, 3, 34),
        (7, 2, 89),
        (7, 3, 98)]];



    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from base import config_str

    engine = create_engine(config_str, echo=True)

    print(Base.metadata.tables.keys()) # 打印所有映射了的表
    Base.metadata.drop_all(engine)     # 删除所有映射了的表
    Base.metadata.create_all(engine)   # 创建所有映射了的表, 如果没有的话
    # 以上两个命令都会直接影响数据库 [begin->commit]

    if False:
        Base.metadata.reflect(engine)      # 获取所有数据库内表的映射
        Base.metadata.reflect(engine, only=['student']) # 获取指定的表

        # NOTE: drop_all 只删除数据库的表, 而不会删除映射, 需要用以下方法删除
        # 仅在映射上删除表, 要实际删除还是需要 drop_all
        Base.metadata.clear()       # 所有当前映射了的表
        table = Student.__table__   # or Base.metadata.tables['student']
        Base.metadata.remove(table) # 单张表

        # print pretty table
        from pprint import pprint
        pprint(list(Student.__table__.c)) # 或 columns

    get_session = sessionmaker(engine)

    #with get_session() as session:
    session = get_session()
    session.add_all(student_lst + course_lst + teacher_lst + sc_lst)
    session.commit()

    # NOTE: student_lst 是绑定到 session 的, 用 with 提交的之后就不能查看了
    # 如果有默认值或 autoincrement, 那么被绑定的 object 就可以实时获得这些值

    if False:

        from sqlalchemy.orm import make_transient
        from sqlalchemy import inspect

        s1 = Student(s_name="张龙", s_birth="1991-11-11")
        session = get_session()
        state = inspect(s1)

        assert s1.s_id is None and s1.s_sex is None
        session.add(s1)
        assert s1.s_id is None and s1.s_sex is None
        session.flush()
        assert s1.s_id is not None and s1.s_sex is not None
        session.commit()

        session.delete(s1)
        assert not state.deleted
        session.flush()
        assert state.deleted
        session.commit()
        assert state.detached

        make_transient(s1)
        session.add(s1)
        session.commit()
