# Version 1.0
# Created by xinyunaha on 2020-12-14 23:45
import bisect
import random
import time

import yaml
import openpyxl


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
        self.GetProbability()
        self.Lottery()
        self.Winner = ''

    def Lottery(self):
        isDrawTime = self.isDrawTime()
        Html_data = []
        if isDrawTime:
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
        if self.config['System']['Excel']:
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
                _user = self.EncryptStr(sheet[f'{LotteryColumn}{a}'].value)
                _width = sheet[f'{WidthColumn}{b}'].value
                if _user is None or _width is None:
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
        else:
            print('非Excel获取数据,退出')

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
        with open('./template.html', '+r', encoding='utf-8') as temp, open(self.config['System']['HTMLPath'], 'w+',
                                                                           encoding='utf-8') as index:
            template = temp.read()
            # ToDo：替换
            t1 = template\
                .replace('%活动截止时间%', '{}'.format(self.config['System']['EndTime'])) \
                .replace('%页面更新时间%', f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}') \
                .replace('%公布结果时间%', '{}'.format(self.config['System']['DrawTime'])) \
                .replace('%奖品设置%', f'{self.GetGifts()}')\
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
        print(nowTime, drawTime)
        if nowTime >= drawTime:
            return True
        else:
            return False

    def EncryptStr(self, data):
        if self.config['System']['EncryptID']:
            _data = str(data).split('@')
            _list = list(_data[0])
            _list[2] = "*"
            _list[3] = "*"
            if len(_data) == 1:
                return "".join(_list)
            else:
                data = ''
                for i in range(len(_data)-1):
                    data += _data[i+1]
                return "".join(_list)+'@'+data
        else:
            return data


if __name__ == '__main__':
    Lottery()
