# Version 1.0
# Created by xinyunaha on 2020-12-14 23:45
import bisect
import random
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


class Lottery:
    def __init__(self):
        self.config = GetConfig()
        self.data = self.GetExcelData()
        self.Lottery()
        self.DatabaseClient = ''

    def Lottery(self):
        for i1 in range(len(self.config['Lottery'])):
            _name = self.config['Lottery'][i1]['name']
            _num = int(self.config['Lottery'][i1]['num'])
            print(f'{_name}获奖名单:')
            for i2 in range(int(_num)):
                print(f'\t{self.GetWinner()}')

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
                _user = sheet[f'{LotteryColumn}{a}'].value
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
            exit()

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


if __name__ == '__main__':
    Lottery()
