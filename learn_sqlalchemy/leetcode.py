from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Date, SmallInteger, DECIMAL
from base import make_repr

Base = declarative_base() # declarative base class


class Stadium(Base):
    __tablename__ = 'Stadium'

    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_date = Column(Date)
    people = Column(Integer)

    def __repr__(self):
        return make_repr(
            self, ["id", "visit_date", "people"], one_row=False)


if True:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from base import config_str

    engine = create_engine(config_str, echo=True)

    print(Base.metadata.tables.keys()) # 打印所有映射了的表
    Base.metadata.drop_all(engine)     # 删除所有映射了的表
    Base.metadata.create_all(engine)   # 创建所有映射了的表, 如果没有的话
    # 以上两个命令都会直接影响数据库 [begin->commit]


    st_col = ["id", "visit_date", "people"]
    st_lst = [Stadium(**dict(zip(st_col, lst))) for lst in [
        (1, "2017-01-01", 10),
        (2, "2017-01-02", 109),
        (3, "2017-01-03", 150),
        (4, "2017-01-04", 99),
        (5, "2017-01-05", 145),
        (6, "2017-01-06", 1455),
        (7, "2017-01-07", 199),
        (8, "2017-01-09", 188)]];

    get_session = sessionmaker(engine)

    #with get_session() as session:
    session = get_session()
    session.add_all(st_lst)
    session.commit()
