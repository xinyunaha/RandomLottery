# Version 1.0
# Created by xinyunaha on 2020-12-14 23:45
import bisect
import random
import time

import openpyxl
import pymysql
import pymysql.cursors
import yaml


def GetConfig():
    try:
        with open("./config.yaml", 'r', encoding='utf-8') as ymlfile:
            f = yaml.load_all(ymlfile, Loader=yaml.SafeLoader)
            for conf in f:
                return conf
    except FileNotFoundError:
        print("未找到文件")
        exit()


def toHtmlTable(data):
    HtmlData = ''
    for item in data:
        HtmlData += '<tr>'
        for i in range(len(item)):
            if item[i] == item[-1]:
                HtmlData += f'<td align="center">{item[i]}</td>'
            else:
                HtmlData += f'<td align="center">{item[i]}</td>'
        HtmlData += '</tr>'
    return HtmlData


class Lottery:
    def __init__(self):
        self.config = GetConfig()
        self.data = self.GetExcelData()
        self.Winner = ''

    def Main(self):
        self.GetProbability()
        self.Lottery()

    def Lottery(self):
        isDrawTime = self.isDrawTime()
        Html_data = []
        if isDrawTime:
            Html_data.append(['奖项', '获奖用户'])
            for data in self.config['Lottery']:
                _name = data['lv_name']
                _num = int(data['num'])
                print(f'{_name}获奖名单:')
                for i2 in range(int(_num)):
                    _winner = self.GetWinner()
                    print(f'\t{_winner}')
                    items = [_name, _winner]
                    Html_data.append(items)
            self.Winner = toHtmlTable(Html_data)
        else:
            print('未到开奖时间')
            self.Winner = '<tr><td>未到开奖时间</td></tr>'
        self.ExportHtml()

    def GetExcelData(self):
        Path = self.config['Excel']['Path']
        LotteryRow = self.config['Excel']['Lottery_Row']
        LotteryColumn = self.config['Excel']['Lottery_Column']
        WidthRow = self.config['Excel']['Width_Row']
        WidthColumn = self.config['Excel']['Width_Column']

        wb = openpyxl.load_workbook(Path)
        names = wb.sheetnames
        sheet = wb[names[0]]
        data = {}
        a = LotteryRow
        b = WidthRow
        while True:
            _user = self.HideStr(sheet[f'{LotteryColumn}{a}'].value)
            _width = None
            if self.config['System']['ExcelWidth']:
                _width = sheet[f'{WidthColumn}{b}'].value
            else:
                _width = self.UserWidth(sheet[f'{LotteryColumn}{a}'].value)
            if _user is None or sheet[f'{WidthColumn}{b}'].value is None:
                break
            else:
                a += 1
                b += 1
            if self.config['System']['Dedupe']:
                try:
                    _ = data[_user]
                    print('数据重复')
                except KeyError:
                    data[_user] = _width
            else:
                data[_user] = _width
        return data

    def UserWidth(self, email):
        width = self.config['System']['BaseWidth']
        if self.config['System']['Verify_Lv']:
            if self.config['System']['Lv_Width']:
                try:
                    userLv = DatabaseHelper().GetUserLv(email)
                    for data in self.config['Width']:
                        if userLv == data['lv']:
                            width += data['add']
                except DatabaseHelper.UserNotFoundException:
                    pass
        else:
            print('不验证')
        return width

    def GetWinner(self):
        keyList = list(self.data.keys())
        valueList = [self.data[key] for key in keyList]
        prefixSum = []
        tmpSum = 0
        for value in valueList:
            tmpSum += value
            prefixSum.append(tmpSum)
        t = random.randint(0, tmpSum - 1)
        Winner = keyList[bisect.bisect_right(prefixSum, t)]
        if self.config['System']['WinOnlyOnce']:
            self.data.pop(Winner)
        return Winner

    def ExportHtml(self):
        print('抽奖完成,导出Html')
        with open('./template.html', '+r', encoding='utf-8') as temp, \
                open(self.config['System']['HTMLPath'], 'w+', encoding='utf-8') as index:
            template = temp.read()
            # ToDo：替换
            t1 = template \
                .replace('%活动截止时间%', '{}'.format(self.config['System']['EndTime'])) \
                .replace('%页面更新时间%', f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}') \
                .replace('%公布结果时间%', '{}'.format(self.config['System']['DrawTime'])) \
                .replace('%奖品设置%', f'{self.GetGifts()}') \
                .replace('%概率公示%', f'{self.GetProbability()}') \
                .replace('%开奖结果%', f'{self.Winner}')
            index.write(t1)

    def GetProbability(self):
        data = self.GetExcelData()
        all_width = 0
        html_data = []
        _user = list(data.keys())
        _width = list(data.values())
        for i in _width:
            all_width += i
        for i in range(len(_user)):
            items = [_user[i], _width[i]]
            html_data.append(items)
        return toHtmlTable(html_data)

    def GetGifts(self):
        html_data = []
        for i in self.config['Lottery']:
            items = [i['lv_name'], i['gifts'], i['num']]
            html_data.append(items)
        return toHtmlTable(html_data)

    def isDrawTime(self):
        nowTime = time.time()
        drawTime = time.mktime(self.config['System']['DrawTime'].timetuple())
        if nowTime >= drawTime:
            return True
        else:
            return False

    def HideStr(self, data):
        if self.config['System']['HideUserID']:
            _data = str(data).split('@')
            _list = list(_data[0])
            _list[2] = "*"
            _list[3] = "*"
            if len(_data) == 1:
                return "".join(_list)
            else:
                data = ''
                for i in range(len(_data) - 1):
                    data += _data[i + 1]
                return "".join(_list) + '@' + data
        else:
            return data


class DatabaseHelper:
    class Error(Exception):
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return self.msg

    class UserNotFoundException(Error):
        """
        用户不存在
        """
        pass

    def __init__(self):
        self.config = GetConfig()['Database']
        self.endTime = time.mktime(GetConfig()['System']['EndTime'].timetuple())
        self.startTime = time.mktime(GetConfig()['System']['StartTime'].timetuple())
        self.connect = pymysql.connect(self.config['Host'],
                                       str(self.config['Username']),
                                       str(self.config['Password']),
                                       self.config['DBName'],
                                       charset='utf8')
        self.cursor = self.connect.cursor()

    def GetUserID(self, email):
        sql = f"select id from user where email='{email}' limit 1;"
        self.cursor.execute(sql)
        self.connect.commit()
        userID = self.cursor.fetchone()
        if userID is None:
            raise self.UserNotFoundException('用户不存在')
        else:
            return userID[0]

    def GetUserLv(self, email):
        sql = f"select class from user where email='{email}' limit 1;"
        self.cursor.execute(sql)
        self.connect.commit()
        lv = self.cursor.fetchone()
        if lv is None:
            raise self.UserNotFoundException('用户不存在')
        else:
            return lv[0]

    def GetUserPay(self, email):
        userid = self.GetUserID(email)
        sql = f"select tradeno from paylist where userid='{userid}' and status=0;"
        self.cursor.execute(sql)
        self.connect.commit()
        data = self.cursor.fetchall()
        payAll = 0.00
        for result in data:
            if result[0] is None:
                pass
            else:
                for pay in result:
                    if self.endTime >= float(pay.split('UID')[0]) >= self.startTime:
                        _sql = f"select total from paylist where tradeno='{pay}';"
                        self.cursor.execute(_sql)
                        self.connect.commit()
                        total = self.cursor.fetchall()
                        payAll += float(total[0][0])
        return payAll


if __name__ == '__main__':
    # print(DatabaseHelper().GetUserLv('test01@test.com'))
    # print(Lottery().GetExcelData())
    Lottery().Main()