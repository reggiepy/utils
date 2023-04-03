# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/9/20 10:35

import datetime
import struct
import time
from functools import wraps


def timer(sys_out=None):
    if sys_out is None:
        sys_out = print

    def _inner(func):
        @wraps(func)
        def __inner(*args, **kwargs):
            start = time.time()
            out = func(*args, **kwargs)
            sys_out(f"Call {func.__name__} Cost {time.time() - start}")
            return out

        return __inner

    return _inner


def DaysMonth(year, month):
    days_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if ((year % 4 == 0 and year % 100 != 0) or year % 400 == 0):
        days_month[1] = 29
    return days_month[month]


def time_call(func):
    @wraps(func)
    def wrap_call(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(TimeNow(), " Call", func.__name__, "Cost", end - start)
        return res

    return wrap_call


class Timer:
    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError("Already started")
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError("Not Started")
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def TimeSeconds(time_stamp, time_format="%Y-%m-%d %H:%M:%S"):
    time_arr = time.strptime(time_stamp, time_format)
    return int(time.mktime(time_arr))


def TimeNow(time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(time.time()))


def GetWeekNumber():
    return datetime.datetime.now().isoweekday()


def SecondToTime(seconds, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(seconds))


def NowSeconds():
    return int(time.time())


def NowMilliseconds():
    """返回毫秒时间戳"""
    return int(time.time() * 1000)


def NowDatetime():
    return datetime.datetime.now()


def NowUTCtime():
    return datetime.datetime.utcnow()


def TimeBeforeNow(seconds, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(time.time() - int(seconds)))


def TimeAfterNow(seconds, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(time.time() + int(seconds)))


def DaysBeforeNow(days, time_format="%Y-%m-%d %H:%M:%S"):
    seconds = 3600 * 24 * days
    return TimeBeforeNow(seconds, time_format=time_format)


def DaysAfterNow(days, time_format="%Y-%m-%d %H:%M:%S"):
    seconds = 3600 * 24 * days
    return TimeAfterNow(seconds, time_format=time_format)


def TimeStampBefore(time_stamp, seconds, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(TimeSeconds(time_stamp) - int(seconds)))


def TimeStampAfter(time_stamp, seconds, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strftime(time_format, time.localtime(TimeSeconds(time_stamp) + int(seconds)))


def Datetime2Int(date_time):
    return time.mktime(date_time.timetuple())


def Datetime2String(date_time, time_format="%Y-%m-%d %H:%M:%S"):
    return date_time.strftime(time_format)


def String2Time(time_str, time_format="%Y-%m-%d %H:%M:%S"):
    return time.strptime(time_str, time_format)


def String2Datetime(time_str, time_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(time_str, time_format)


def String2Second(time_str, time_format="%Y-%m-%d %H:%M:%S"):
    timeArray = time.strptime(time_str, time_format)
    return int(time.mktime(timeArray))


def TimeBCD():
    timestr = TimeNow()
    year = struct.pack("B", int(timestr[2:4]))
    mon = struct.pack("B", int(timestr[5:7]))
    day = struct.pack("B", int(timestr[8:10]))
    hour = struct.pack("B", int(timestr[11:13]))
    min = struct.pack("B", int(timestr[14:16]))
    sec = struct.pack("B", int(timestr[17:19]))
    return sec + min + hour + day + mon + year


def FirstDay2Month(month_delta=0):
    # 获取当月第一天，month_delta = -1， 上个月第一天，month_delta=1， 下个月第一天
    curTime = datetime.date.today()
    year_delta = 0
    if month_delta + curTime.month > 12 or month_delta + curTime.month < 1:
        year_delta = (month_delta + curTime.month) / 12
        if (month_delta + curTime.month) % 12 == 0:
            year_delta -= 1
            month_delta = 12 - curTime.month
        else:
            month_delta = month_delta - (month_delta + curTime.month) / 12 * 12
    firstDay = datetime.datetime(year=curTime.year + year_delta, month=curTime.month + month_delta, day=1, hour=0,
                                 minute=0, second=0)
    return firstDay


def LastDay2Month(month_delta=-1):
    # 获取当月最后一天
    lastMonthFirstDay = FirstDay2Month(month_delta=month_delta + 1)
    lastDay = lastMonthFirstDay - datetime.timedelta(days=1)
    return lastDay.replace(hour=23, minute=59, second=59)


def FirstDay2Week(week_delta=0):
    # 获取当周的第一天（周一）
    weekNum = datetime.datetime.now().weekday()
    Monday = datetime.datetime.now() + datetime.timedelta(days=-weekNum + week_delta * 7)
    return Monday.replace(hour=0, minute=0, second=0, microsecond=0)


def LastDay2Week(week_delta=-1):
    # 获取当周的最后一天（周日）
    weekNum = datetime.datetime.now().weekday()
    Sunday = datetime.datetime.now() + datetime.timedelta(days=week_delta * 7 + 6 - weekNum)
    return Sunday.replace(hour=23, minute=59, second=59, microsecond=0)


def LastDay(days=-1):
    return (datetime.datetime.now() + datetime.timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)


def MonthBefore(month_before=1, month_after=0):
    # 返回month_before个自然月前第一天日期
    time_now = datetime.datetime.now()
    time_now = datetime.datetime(time_now.year, time_now.month, 1, 0, 0, 0)
    year = time_now.year
    month = time_now.month
    days = 0
    for i in range(0, month_before):
        month -= 1
        if month <= 0:
            year -= 1
            month = 12
        days += DaysMonth(year, month - 1)
    return time_now - datetime.timedelta(days=days)


def month_addorsub(start_time, count, add=0, time_format="%Y-%m-%d %H:%M:%S"):
    '''
    返回指定时间几个月前或后一个号的日期
    start_time: string
    count: 几个月，int
    add: 0，前；1，后
    '''
    start_time = datetime.datetime.strptime(start_time, time_format)
    year = start_time.year
    month = start_time.month
    days = 0
    for i in range(0, count):
        if add:
            days += DaysMonth(year, month - 1)
            if month == 12:
                year += 1
                month = 1
            else:
                month += 1
        else:
            if month == 1:
                year -= 1
                month = 12
            else:
                month -= 1
            days += DaysMonth(year, month - 1)
    if add:
        return start_time + datetime.timedelta(days=days)
    return start_time - datetime.timedelta(days=days)


def month_end(start_time, time_format="%Y-%m-%d %H:%M:%S"):
    '''
    返回指定月月末的日期
    start_time: string
    '''
    start_time = datetime.datetime.strptime(start_time, time_format)
    year = start_time.year
    month = start_time.month
    days = DaysMonth(year, month - 1) - 1
    end_time = start_time + datetime.timedelta(days=days)
    end_time = datetime.datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)
    return end_time


def YearBefore(year_before=1):
    # 返回year_before个自然年前第一天日期
    year = datetime.datetime.now().year
    return datetime.datetime(year - year_before, 1, 1, 0, 0, 0)


def DateTimeFormat(date_time, format_string="%Y-%m-%d %H:%M:%S"):
    # 将时间格式化
    if not date_time:
        date_time = datetime.datetime.now()
    return date_time.strftime(format_string)


def Utc2TimeStamp(utc_string):
    # get local time zone name
    utc_string = utc_string[:utc_string.rfind(".")].replace("T", " ")
    return SecondToTime(TimeSeconds(utc_string))


def TimeStr2Utc(time_str, time_format="%Y-%m-%d %H:%M:%S"):
    TIME_FORMAT = time_format
    local_time = datetime.datetime.strptime(time_str, TIME_FORMAT)
    local_time = local_time + datetime.timedelta(hours=-8)
    utc_time = datetime.datetime.strftime(local_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    print(utc_time)
    return utc_time


def Utc2TimeStr(utc_str):
    UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ" if utc_str.find(".") > 0 else "%Y-%m-%dT%H:%M:%SZ"
    utc_time = datetime.datetime.strptime(utc_str, UTC_FORMAT)
    local_time = utc_time + datetime.timedelta(hours=8)
    print(local_time)
    return local_time


def TimeSubSeconds(t1, t2):
    t1, t2 = String2Datetime(t1), String2Datetime(t2)
    return float((t1 - t2).seconds)


def TimeSubMinutes(t1, t2):
    return TimeSubSeconds(t1, t2) / 60


def TimeSubHours(t1, t2):
    return TimeSubMinutes(t1, t2) / 60


def TimeSubDays(t1, t2):
    return TimeSubHours(t1, t2) / 24


def test():
    d = datetime.datetime.now()
    print(Datetime2String(d))
    print(TimeNow())
    print(TimeStampBefore("2017-12-11 12:00:00", 59))
    print(TimeBeforeNow(30))
    print(SecondToTime(1489991675))
    print(FirstDay2Month(-12 + 1))
    print(LastDay2Month(0), LastDay2Month(-2))
    print(FirstDay2Week(), FirstDay2Week(-2))
    print(LastDay2Week(-2), LastDay2Week(0))
    print(LastDay(), LastDay(-2))


def test_2():
    utc_str = "2018-09-12T12:00:00Z"
    Utc2TimeStr(utc_str)
    time_str = "2018-09-12 12:00:00"
    TimeStr2Utc(time_str)


def test_3():
    def counterdown(n):
        while n > 0:
            n -= 1

    t = Timer()
    t.start()
    counterdown(10000000)
    t.stop()
    print(t.elapsed)

    with t:
        counterdown(10000000)
    print(t.elapsed)

    with Timer() as t2:
        counterdown(10000000)
    print(t2.elapsed)

    with Timer(time.process_time) as t3:
        counterdown(10000000)
    print(t3.elapsed)


if __name__ == '__main__':
    TimeNow()
    # print Utc2TimeStamp("2018-11-29T07:53:56.566551893Z")
    # test_2()
    # ms2t(72105281)
    # test_3()
    # print(TimeSubDays(TimeNow(), "2021-01-18 20:30:04"))
    # print(TimeNow())
    print(SecondToTime(1623385891))
    # print(SecondToTime(time.time()))
    # time_format = "%Y-%m-%d"
    # print(SecondToTime(String2Second(SecondToTime(time.time())), time_format=time_format))
    # print(String2Second("2021-01-18 20:30:04"))
    date = 1629875992
    start_time = SecondToTime(date, time_format="%Y-%m-%d 00:00:00")
    stop_time = SecondToTime(date, time_format="%Y-%m-%d 23:59:59")
    print(start_time, stop_time)
    print(String2Second(start_time), String2Second(stop_time))
    print(SecondToTime(String2Second(start_time)), SecondToTime(String2Second(stop_time)))
