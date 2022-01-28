def p01(session):
    subquery = session\
        .query(SC)\
        .filter(SC.c_id == 2)\
        .subquery()
    res = (session
           .query(Student, SC.score, subquery.c.score)
           .filter(SC.c_id == 1)
           .join(subquery, SC.s_id == subquery.c.s_id)
           .filter(SC.score > subquery.c.score)
           .join(Student, SC.s_id == Student.s_id)
           .all())
    pprint(res)

def p01_1(session):
    subquery = (session
                .query(SC)
                .filter(SC.c_id == 2)
                .subquery())
    res = (session
           .query(SC.s_id, SC.score, subquery.c.score)
           .filter(SC.c_id == 1)
           .join(subquery, SC.s_id == subquery.c.s_id)
           .all())
    pprint(res)

def p01_2(session):
    subquery = (session
                .query(SC)
                .filter(SC.c_id == 2)
                .subquery())
    res = (session
           .query(SC.s_id, SC.score, subquery.c.score)
           .filter(SC.c_id == 1)
           .outerjoin(subquery, SC.s_id == subquery.c.s_id)
           .all())
    pprint(res)

def p01_3(session):
    query = (session # NOTE: not a subquery
             .query(SC.s_id)
             .filter(SC.c_id == 1))
    res = (session
           .query(SC.s_id, SC.score)
           .filter(SC.c_id == 2)
           .filter(SC.s_id.not_in(query))
           .all())
    pprint(res)

def p02(session):
    avg_score = func.avg(SC.score).label('avg_score')
    subquery = (session
                .query(SC.s_id, avg_score)
                .group_by(SC.s_id)
                .having(avg_score > 60)
                .subquery())
    res = (session
           .query(Student.s_id, Student.s_name, subquery.c.avg_score)
           .join(subquery, Student.s_id == subquery.c.s_id)
           .all())
    pprint(res)

def p03(session):
    res = (session
           .query(Student)
           .filter(exists().where(Student.s_id == SC.s_id))
           .all())
    pprint(res)

def p04(session):
    subquery = (session
                .query(SC.s_id,
                       func.count("*").label("c_count"),
                       func.sum(SC.score).label("s_score"))
                .group_by(SC.s_id)
                .subquery())
    res = (session
           .query(Student.s_id, Student.s_name, subquery.c.c_count, subquery.c.s_score)
           .outerjoin(subquery, Student.s_id == subquery.c.s_id)
           .all())
    pprint(res)

def p04_1(session):
    res = (session
           .query(Student)
           .filter(exists().where(SC.s_id == Student.s_id))
           .all())
    pprint(res)

def p05(session):
    res = (session
           .query(Teacher)
           .filter(Teacher.t_name.like("李%"))
           .count())
    #.scalar()) # NOTE: no scalar
    pprint(res)

def p06(session):
    query = (session
             .query(distinct(SC.s_id))
             .join(Course, Course.c_id == SC.c_id)
             .join(Teacher, Course.t_id == Teacher.t_id)
             .filter(Teacher.t_name == "张三"))
    res = (session
           .query(Student)
           .filter(Student.s_id.in_(query))
           .all())
    pprint(res)

def p07(session):
    course_total = (session
                    .query(Course)
                    .count())
    query = (session
             .query(SC.s_id)
             .group_by(SC.s_id)
             .having(func.count("*") == course_total))
    res = (session
           .query(Student)
           .filter(Student.s_id.not_in(query))
           .all())
    pprint(res)

def p08(session):
    subquery = (session
                .query(SC)
                .filter(SC.s_id == 1)
                .subquery())
    res = (session
           .query(Student)
           .distinct()
           .filter(Student.s_id != 1)
           .join(SC, Student.s_id == SC.s_id)
           .filter(exists().where(subquery.c.c_id == SC.c_id))
           .all())
    pprint(res)

def p09(session):
    s1_learned = (session
                  .query(func.group_concat(SC.c_id))
                  .filter(SC.s_id == 1)
                  .scalar())
    query = (session
             .query(SC.s_id)
             .filter(SC.s_id != 1)
             .group_by(SC.s_id)
             .having(func.group_concat(SC.c_id) == s1_learned))
    res = (session
           .query(Student)
           .filter(Student.s_id.in_(query))
           .all())
    pprint(res)

def p10(session):
    rows = (session
            .query(Course.c_id)
            .join(Teacher, Course.t_id == Teacher.t_id)
            .filter(Teacher.t_name == "张三")
            .all())
    c_id_z3 = [row.c_id for row in rows]
    # 这里试着把查询结果做出来, 也不知道哪种方法更好
    query = (session
             .query(SC.s_id)
             .distinct()
             .filter(SC.c_id.in_(c_id_z3)))
    res = (session
           .query(Student.s_name)
           .filter(Student.s_id.not_in(query))
           .all())
    pprint(res)

def p11(session):
    avg_score = func.avg(SC.score).label("avg_score")
    # 这句也可以放到下面的 subquery 里
    subquery = (session
                .query(SC.s_id, avg_score)
                .group_by(SC.s_id)
                .subquery())
    s_id_needed = (session
                   .query(SC.s_id)
                   .filter(SC.score < 60)
                   .group_by(SC.s_id)
                   .having(func.count("*") > 1))
    res = (session
           .query(Student.s_id, Student.s_name, subquery.c.avg_score)
           .join(subquery, Student.s_id == subquery.c.s_id)
           .filter(Student.s_id.in_(s_id_needed))
           .all())
    pprint(res)

def p12(session):
    subquery = (session
                .query(SC.s_id, SC.score)
                .filter(and_(SC.c_id == 1, SC.score < 60))
                .subquery())
    res = (session
           .query(Student)
           .join(subquery, Student.s_id == subquery.c.s_id)
           .order_by(desc(subquery.c.score))
           .all())
    pprint(res)

def p13(session):
    avg_score = func.avg(SC.score).label("avg_score")
    subquery = (session
                .query(SC.s_id, avg_score)
                .group_by(SC.s_id)
                .subquery())
    res = (session
           .query(SC, subquery.c.avg_score)
           .join(subquery, SC.s_id == subquery.c.s_id)
           .order_by(desc(subquery.c.avg_score), SC.s_id, SC.c_id)
           .all())
    pprint(res)

def p14(session):
    # NOTE: 我一开始 label 写重了, 但没有报错, 甚之
    # TODO: 这里的 count 是不是重复计算, 如何解决
    s_max = func.max(SC.score).label("最高分")
    s_min = func.min(SC.score).label("最低分")
    s_avg = func.avg(SC.score).label("平均分")
    s_count = func.count("*").label("s_count")
    s_d = (func.sum(func.if_(SC.score >= 60, 1, 0)) / s_count).label("及格率")
    s_c = (func.sum(func.if_(and_(SC.score >= 70, SC.score < 80), 1, 0))
           / s_count).label("中等率")
    s_b = (func.sum(func.if_(and_(SC.score >= 80, SC.score < 90), 1, 0))
           / s_count).label("优良率")
    s_a = (func.sum(func.if_(SC.score >= 90, 1, 0)) / s_count).label("优秀率")
    res = (session
           .query(SC.c_id, Course.c_name, s_max, s_min, s_avg,
                  s_d, s_c, s_b, s_a)
           .join(Course, SC.c_id == Course.c_id)
           .group_by(SC.c_id)
           .order_by(desc(s_count), SC.c_id)
           .all())
    pprint(res)

def p15(session):
    s_rank = func.rank().over(partition_by=SC.c_id, order_by=desc(SC.score))
    res = (session
           .query(SC.c_id, SC.s_id, SC.score, s_rank)
           .order_by(SC.c_id, s_rank)
           .all())
    pprint(res)

def p15_1(session):
    s_rank = func.dense_rank().over(
        partition_by=SC.c_id, order_by=desc(SC.score))
    res = (session
           .query(SC.c_id, SC.s_id, SC.score, s_rank)
           .order_by(SC.c_id, s_rank)
           .all())
    pprint(res)

def p16(session):
    t_score = func.sum(SC.score).label("t_score")
    s_rank = func.rank().over(order_by=desc(t_score))
    res = (session
           .query(SC.s_id, t_score, s_rank)
           .group_by(SC.s_id)
           .order_by(desc(t_score))
           .all())
    pprint(res)

def p16_1(session):
    t_score = func.sum(SC.score).label("t_score")
    s_rank = func.dense_rank().over(order_by=desc(t_score))
    res = (session
           .query(SC.s_id, t_score, s_rank)
           .group_by(SC.s_id)
           .order_by(desc(t_score))
           .all())
    pprint(res)

def p17(session):
    t_score = func.sum(SC.score)
    s_a = func.sum(func.if_(SC.score >= 85, 1, 0))
    s_b = func.sum(func.if_(and_(SC.score >= 70, SC.score < 85), 1, 0))
    s_c = func.sum(func.if_(and_(SC.score >= 60, SC.score < 70), 1, 0))
    s_d = func.sum(func.if_(SC.score < 60, 1, 0))
    s_count = func.count("*")
    res = (session
           .query(SC.c_id, Course.c_name, s_a, s_a/s_count,
                  s_b, s_b/s_count, s_c, s_c/s_count, s_d, s_d/s_count)
           .join(Course, SC.c_id == Course.c_id)
           .group_by(SC.c_id)
           .all())
    pprint(res)

def p18(session):
    s_rank = func.rank().over(
        partition_by=SC.c_id, order_by=desc(SC.score)).label("s_rank")
    subquery = (session
                .query(SC.c_id, SC.s_id, SC.score, s_rank)
                .subquery())
    res = (session
           .query(subquery)
           .filter(subquery.c.s_rank < 4)
           .all())
    pprint(res)

def p19(session):
    res = (session
           .query(SC.c_id, func.count(SC.s_id))
           .group_by(SC.c_id)
           .all())
    pprint(res)

def p20(session):
    query = (session
             .query(SC.s_id)
             .group_by(SC.s_id)
             .having(func.count(SC.c_id) == 2))
    res = (session
           .query(Student.s_id, Student.s_name)
           .filter(Student.s_id.in_(query))
           .all())
    pprint(res)

def p21(session):
    res = (session
           .query(Student.s_sex, func.count("*"))
           .group_by(Student.s_sex)
           .all())
    pprint(res)

def p22(session):
    res = (session
           .query(Student)
           .filter(Student.s_name.like("%风%"))
           .all())
    pprint(res)

def p24(session):
    res = (session
           .query(Student)
           .filter(func.year(Student.s_birth) == 1990)
           .all())
    pprint(res)

def p25(session):
    avg_score = func.avg(SC.score).label("avg_score")
    res = (session
           .query(SC.c_id, avg_score)
           .group_by(SC.c_id)
           .order_by(desc(avg_score), SC.c_id)
           .all())
    pprint(res)

def p26(session):
    avg_score = func.avg(SC.score).label("avg_score")
    subquery = (session
                .query(SC.s_id, avg_score)
                .group_by(SC.s_id)
                .having(avg_score > 85)
                .subquery())
    res = (session
           .query(Student.s_id, Student.s_name, subquery.c.avg_score)
           .join(subquery, Student.s_id == subquery.c.s_id)
           .all())
    pprint(res)


def p27(session):
    query = (session
             .query(Course.c_id)
             .filter(Course.c_name == "数学"))
    res = (session
           .query(Student.s_name, SC.score)
           .join(SC, Student.s_id == SC.s_id)
           .filter(SC.c_id.in_(query))
           .filter(SC.score < 60)
           .all())
    pprint(res)

def p28(session):
    query = (session
             .query(Course.c_id)
             .filter(Course.c_name == "数学"))
    res = (session
           .query(Student, SC.c_id, SC.score)
           .outerjoin(SC, Student.s_id == SC.s_id)
           .all())
    pprint(res)

def p29(session):
    query = (session
             .query(SC.s_id)
             .distinct()
             .filter(SC.score >= 70))
    res = (session
           .query(Student.s_name, Course.c_name, SC.score)
           .join(Student, SC.s_id == Student.s_id)
           .join(Course, SC.c_id == Course.c_id)
           .filter(SC.s_id.in_(query))
           .all())
    pprint(res)

def p31(session):
    query = (session
             .query(SC.s_id)
             .filter(SC.c_id == 1)
             .filter(SC.score >= 80))
    res = (session
           .query(Student.s_id, Student.s_name)
           .filter(Student.s_id.in_(query))
           .all())
    pprint(res)

def p32(session):
    res = (session
           .query(SC.c_id, func.count("*"))
           .group_by(SC.c_id)
           .all())
    pprint(res)

def p33(session):
    query = (session
             .query(Course.c_id)
             .join(Teacher, Course.t_id == Teacher.t_id)
             .filter(Teacher.t_name == "张三"))
    row = (session
           .query(SC.s_id, SC.score)
           .filter(SC.c_id.in_(query))
           .order_by(desc(SC.score))
           .limit(1)
           .first())
    res = (session
           .query(Student, row.score)
           .filter(Student.s_id == row.s_id)
           .first())
    pprint(res)

def p34(session):
    query = (session
             .query(Course.c_id)
             .join(Teacher, Course.t_id == Teacher.t_id)
             .filter(Teacher.t_name == "张三"))
    zhang = (session
             .query(SC.s_id, SC.score)
             .filter(SC.c_id.in_(query))
             .cte())
    query_max = (session
                 .query(func.max(zhang.c.score)))
    res = (session
           .query(Student, zhang.c.score)
           .join(zhang, Student.s_id == zhang.c.s_id)
           .filter(zhang.c.score == query_max)
           .all())
    pprint(res)

def p35(session):
    query = (session
             .query(SC.c_id, SC.score)
             .group_by(SC.c_id, SC.score)
             .having(func.count("*") > 1))
    res = (session
           .query(SC)
           .filter(tuple_(SC.c_id, SC.score).in_(query))
           .all())
    pprint(res)


def p36(session):
    s_rank = func.rank().over(partition_by=SC.c_id, order_by=desc(SC.score)).label("s_rank")
    subquery = (session
             .query(SC.c_id, SC.s_id, SC.score, s_rank)
             .subquery())
    res = (session
             .query(subquery)
             .filter(subquery.c.s_rank < 3)
             .all())
    pprint(res)


def p37(session):
    c_count = func.count("*").label("c_count")
    res = (session
           .query(SC.c_id, c_count)
           .group_by(SC.c_id)
           .having(c_count > 5)
           .all())
    pprint(res)


def p38(session):
    res = (session
           .query(SC.s_id)
           .group_by(SC.s_id)
           .having(func.count("*") > 1)
           .all())
    pprint(res)

def p39(session):
    c_count = (session
               .query(func.count("*"))
               .select_from(Course)
               .scalar())
    res = (session
           .query(Student)
           .join(SC, Student.s_id == SC.s_id)
           .group_by(SC.s_id)
           .having(func.count(SC.c_id) == c_count)
           .all())
    pprint(res)

def p40(session):
    res = (session
           .query(*Student.__table__.c,
                  func.year(func.now()) - func.year(Student.s_birth))
           .all())
    pprint(res)

def p41(session):
    res = (session
           .query(*Student.__table__.c,
                  func.year(func.now()) - func.year(Student.s_birth)
                    - func.if_(func.month(func.now()) * 100 + func.day(func.now())
                               < func.month(Student.s_birth) * 100 + func.day(Student.s_birth), 1, 0))
           .all())
    pprint(res)

def p42_1(session):
    res = (session
           .query(Student)
           .filter(func.weekofyear(func.now()) == func.weekofyear(Student.s_birth))
           .all())
    pprint(res)


def p42_2(session):
    res = (session
           .query(Student)
           .filter(func.weekofyear(func.date_add(func.now(), text('interval 7 day'))) == func.weekofyear(Student.s_birth))
           .all())
    pprint(res)


def p42_3(session):
    res = (session
           .query(Student)
           .filter(func.month(func.now()) == func.month(Student.s_birth))
           .all())
    pprint(res)

def p42_4(session):
    res = (session
           .query(Student)
           .filter(func.month(func.date_add(func.now(), text('interval 1 month'))) == func.month(Student.s_birth))
           .all())
    pprint(res)
