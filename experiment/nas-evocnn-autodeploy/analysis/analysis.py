import os
import sys
import csv
import re
import pandas as pd

class RunnerAnalysis(object):
    pass

testData = """indi00048_00020.ncnn.param  min =   0.131  max =   0.303  avg =   0.139
times: 0.178 0.225 0.179 0.198 0.132 0.131 0.132 0.131 0.132 0.132 0.132 0.303 0.217 0.132 0.133 0.132 0.133 0.131 0.180 0.132 0.132 0.131 0.131 0.133 0.132 0.131 0.133 0.132 0.132 0.132 0.132 0.132 0.132 0.131 0.132 0.132 0.132 0.133 0.132 0.131 0.131 0.132 0.132 0.132 0.132 0.132 0.131 0.164 0.150 0.132 0.131 0.132 0.132 0.132 0.132 0.132 0.133 0.132 0.131 0.132 0.133 0.131 0.132 0.132 0.132 0.131 0.132 0.131 0.132 0.132 0.132 0.132 0.133 0.132 0.132 0.132 0.133 0.194 0.132 0.132 0.132 0.132 0.132 0.131 0.132 0.132 0.132 0.132 0.132 0.132 0.132 0.132 0.162 0.136 0.135 0.135 0.135 0.135 0.135 0.135 0.136 0.135 0.136 0.135 0.135 0.135 0.187 0.136 0.136 0.135 0.136 0.135 0.135 0.135 0.135 0.136 0.135 0.134 0.134 0.135 0.135 0.135 0.136 0.135 0.136 0.136 0.136 0.135 0.136 0.152 0.238 0.198 0.135 0.135 0.180 0.151 0.135 0.135 0.136 0.134 0.135 0.135 0.135 0.135 0.136 0.135 0.135 0.136 0.135 0.135 0.136 0.134 0.135 0.134 0.136 0.136 0.136 0.134 0.136 0.136 0.135 0.135 0.139 0.182 0.135 0.136 0.136 0.135 0.134 0.134 0.136 0.136 0.135 0.136 0.136 0.135 0.135 0.136 0.135 0.135 0.135 0.135 0.136 0.136 0.136 0.136 0.135 0.135 0.136 0.134 0.136 0.165 0.152 0.135 0.136 0.135 0.136 0.136 0.135 0.135"""

timesPattern = re.compile(r'(indi[\w.]*)[\w*=. ]*\ntimes:([\d. ]+)')

def analysisOneRunner_times(timesResult :str) -> float:

    itemRunnerTimes = [float(item) for item in timesResult.strip().split(" ")]
    _timeCalSum = 0.0
    for idx, timeVal in enumerate(itemRunnerTimes):
        _timeCalSum += timeVal
    
    timeCalAvg = _timeCalSum / len(itemRunnerTimes)

    pdDatas = {
        "times": pd.Series(itemRunnerTimes)
    }

    df = pd.DataFrame(pdDatas)

    # print("item", itemName, itemRunnerTimesStr)
    # print("times", itemRunnerTimes)

    # print("AVG", timeCalAvg)

    # print(df['times'].value_counts())

    # print(df.describe())

    # print("median")
    print(df.median())

    return 0

def analysisOneRunnerResult(result :str) -> int:
    print(result)

    # #pattern = re.compile(r'indi[\w.]*')   # 查找数字
    # pattern = re.compile(r'(indi[\w.]*)[\w*=. ]*\ntimes:([\d. ]+)')   # 查找数字
    # reResult = pattern.search(testData)

    ret = re.search(timesPattern, result)
    # 没有找到则为空
    if ret is None:
        print("string [%s] not searched" % result)
        return -1

    # print("ret", ret)
    # print("*"*20)
    # print(ret.group())
    # print("*"*20)
    # print(ret[1])
    # print(ret[2])
    # print("!"*20)

    # #reResult = reResult[0]
    # print(reResult, reResult[0])
    # return 0
    # if len(reResult) == 0:
    #     return -1

    # itemName = reResult[0]
    # itemRunnerTimesStr = reResult[1].strip()

    itemName = ret[1]
    itemRunnerTimesStr = ret[2]

    analysisOneRunner_times(itemRunnerTimesStr)



if __name__ == '__main__':

    f = open("data2.txt",'r',encoding='utf-8')
    fileLines = f.readlines()
    f.close()

    flag = 0
    for line in fileLines:
        if flag == 0:
            if "!@#$beginbenchmark$#@!" in line:
                flag = 1
            continue

        print(line)
        #csvRow = line.split()
        #writer.writerow(csvRow)

        expItems = re.findall(timesPattern, "".join(fileLines))

        print(expItems)

        for item in expItems:
            print("="*20)
            print("name", item[0])
            analysisOneRunner_times(item[1])
        break


    print("*"*20)

    #analysisOneRunnerResult(testData)


    # a = re.findall("[^a-z]", "匹配s规则这s个字符串是否s匹配f规则则re则则则")


