import pymysql
import os
import json
from bottle import route, run, static_file, request, BaseRequest, template, response
import bottle
import time
import datetime

HOST = '127.0.0.1'
USER = 'root'
PASSWORD = ''
PORT = 3306


def dateRange(beginDate, endDate):
    dates = []
    dt = datetime.datetime.strptime(beginDate, "%Y-%m-%d")
    date = beginDate[:]
    while date <= endDate:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates


def allow_cross_domain(fn):
    def _enable_cors(*args, **kwargs):
        # set cross headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,OPTIONS'
        allow_headers = 'Referer, Accept, Origin, User-Agent'
        response.headers['Access-Control-Allow-Headers'] = allow_headers
        if bottle.request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)
    return _enable_cors


class KsCanteenDao:
    def __init__(self, host, port, user, pwd, db_name):
        self.conn = pymysql.connect(host=host, user=user, passwd=pwd,
                                    port=port, db=db_name, charset='utf8')
        self.conn.autocommit(1)
        # self.init_table()

    def init_table(self):
        sql = """create table if not exists ks_canteen (
            foodId int not null,
            name  varchar(64) not null,
            mealTimeType varchar(16) not null,  
            likeCount int not null default 0,
            dislikeCount int not null default 0,
            dayOfWeek int not null,
            date date not null,
            unique key id_mtype_date(foodId,mealTimeType,date)
            )
        """
        self.__exec(sql)

    def insert_data(self, foodId, name, mealTimeType, likeCount, dislikeCount, dayOfWeek, date):
        sql = """insert into ks_canteen values(%d,'%s','%s',%d,%d,%d,'%s')""" % (
            foodId, name, mealTimeType, likeCount, dislikeCount, dayOfWeek, date)
        self.__exec(sql)

    def get_dayOfWeek_count(self, name):
        sql = """select dayOfWeek, count(1)  from ks_canteen where name='%s' group by dayOfWeek;""" % name
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        from  decimal import Decimal
        return rets

    def get_all_name(self):
        sql = 'select distinct name from ks_canteen'
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        return list(map(lambda x: x[0], rets))

    def get_date_appear(self, name):
        sql = """select date from ks_canteen where name='%s' group by date order by date
 asc""" % (name)
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        return list(map(lambda x: x[0].strftime("%Y-%m-%d"), rets))

    def get_like_dislike_count(self, name):
        sql = """select sum(likeCount),sum(dislikeCount) from ks_canteen where name='%s';"""%name
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchone()
        return [int(str(rets[0])), int(str(rets[1]))]

    def get_all_like_count(self, nums):
        sql = """select name,sum(likeCount) as s from ks_canteen group by name order by s desc limit %d;"""%nums
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        return rets
    
    def get_all_dislike_count(self, nums):
        sql = """select name,sum(dislikeCount) as s from ks_canteen group by name order by s desc limit %d;"""%nums
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        return rets

    def get_foodId_count(self):
        sql = """select count(distinct foodId) from ks_canteen;"""
        cur = self.conn.cursor()
        cur.execute(sql)
        ret = cur.fetchone()
        return int(str(ret[0]))

    def get_dishes_count(self):
        sql = """select count(1) from ks_canteen;"""
        cur = self.conn.cursor()
        cur.execute(sql)
        ret = cur.fetchone()
        return int(str(ret[0]))

    def get_dayOfWeek_high_rate(self, dayOfWeek):
        sql = """select name, count(1) as c from ks_canteen where dayOfWeek=%d and mealTimeType<>'BREAKFAST' group by name having c> 5 order by c desc;"""%dayOfWeek
        cur = self.conn.cursor()
        cur.execute(sql)
        rets = cur.fetchall()
        return rets


    def __exec(self, sql):
        print(sql)
        self.conn.cursor().execute(sql)

    def close(self):
        self.conn.close()


def get_files_fullpath(dir_path, suffix=''):
    files = list(filter(lambda x: os.path.isfile(
        os.path.join(dir_path, x)), os.listdir(dir_path)))
    if suffix != '':
        files = list(filter(lambda x: x.endswith(suffix), files))
    all_fullpath = list(map(lambda x: os.path.join(dir_path, x), files))
    return all_fullpath


def save_all_data():
    dao = KsCanteenDao(HOST, PORT, USER, PASSWORD, 'shuogg')
    f_paths = get_files_fullpath('mealMenu')
    for p in f_paths:
        with open(p, 'r', encoding='utf8') as f:
            text = f.read()
            j = json.loads(text)
            data = j['data']
            date = data['date']
            detail = data['detail']
            dayOfWeek = detail['dayOfWeek']
            mealFoods = detail['mealFoods']
            for food in mealFoods:
                dao.insert_data(food['id'], food['name'], food['mealTimeType'],
                                food['likeCount'], food['dislikeCount'], dayOfWeek, date)

    dao.close()


dao = KsCanteenDao(HOST, PORT, USER, PASSWORD, 'shuogg')


@route('/food/names', method='GET')
@allow_cross_domain
def food_names():
    return json.dumps(all_names, ensure_ascii=False)


@route('/food/dayofweek/count', method='GET')
@allow_cross_domain
def dayOfWeekCounts():
    name = bottle.request.query.decode('utf8').get('name')
    rets = dao.get_dayOfWeek_count(name)
    cnt_list = [0, 0, 0, 0, 0, 0, 0]
    for (d, cnt) in rets:
        cnt_list[d-1] = cnt
    return json.dumps(cnt_list, ensure_ascii=False)


@route('/food/date/count', method='GET')
@allow_cross_domain
def foodDateCnt():
    name = bottle.request.query.decode('utf8').get('name')
    dates = dateRange('2019-04-02', '2019-07-31')
    date_cnt_list = [0] * len(dates)
    dates_food = dao.get_date_appear(name)
    if len(dates_food) == 0:
        return json.dumps({
            'dates': dates,
            'counts': date_cnt_list,
        }, ensure_ascii=False)
    df_index = 0
    for (d, i) in zip(dates, range(len(dates))):
        if d == dates_food[df_index]:
            df_index += 1
            date_cnt_list[i] = 1
            if df_index >= len(dates_food):
                break
    return json.dumps({
        'dates': dates,
        'counts': date_cnt_list,
    }, ensure_ascii=False)

@route('/food/likedislike/count', method='GET')
@allow_cross_domain
def food_like_dislike_cnt():
    name = bottle.request.query.decode('utf8').get('name')
    counts = dao.get_like_dislike_count(name)
    return json.dumps(counts, ensure_ascii=False)

@route('/all/like/count', method='GET')
@allow_cross_domain
def all_like_cnt():
    names = []
    counts = []
    for (name,count) in like_cnt:
        names.append(name)
        counts.append(int(str(count)))
    return json.dumps({
        'names':names,
        'counts':counts
    }, ensure_ascii=False)

@route('/all/dislike/count', method='GET')
@allow_cross_domain
def all_dislike_cnt():
    names = []
    counts = []
    for (name,count) in dislike_cnt:
        names.append(name)
        counts.append(int(str(count)))
    return json.dumps({
        'names':names,
        'counts':counts
    }, ensure_ascii=False)

@route('/all/count', method='GET')
@allow_cross_domain
def all_cnt():
    return json.dumps([foodId_cnt, dish_cnt], ensure_ascii=False)

@route('/dayofweek/lt5', method='GET')
@allow_cross_domain
def dayOfWeekRateLt5():
    names = []
    counts = []
    dayOfWeek = bottle.request.query.decode('utf8').get('day')
    ret = dao.get_dayOfWeek_high_rate(int(dayOfWeek))
    for (name,count) in ret:
        names.append(name)
        counts.append(int(str(count)))
    return json.dumps({
        'names':names,
        'counts':counts
    }, ensure_ascii=False)

all_names = dao.get_all_name()
like_cnt = dao.get_all_like_count(15)
foodId_cnt = dao.get_foodId_count()
dish_cnt = dao.get_dishes_count()
dislike_cnt = dao.get_all_dislike_count(15)
print('start server...')
run(host="10.13.145.72", port=8888)