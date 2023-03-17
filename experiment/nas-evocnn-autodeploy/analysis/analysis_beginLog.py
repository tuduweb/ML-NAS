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



def get_file(file_path: str, suffix: str, res_file_path: list) -> list:
    """获取路径下的指定文件类型后缀的文件

    Args:
        file_path: 文件夹的路径
        suffix: 要提取的文件类型的后缀
        res_file_path: 保存返回结果的列表

    Returns: 文件路径

    """

    for file in os.listdir(file_path):

        if os.path.isdir(os.path.join(file_path, file)):
            get_file(os.path.join(file_path, file), suffix, res_file_path)
        else:
            res_file_path.append(os.path.join(file_path, file))

    # endswith：表示以suffix结尾。可根据需要自行修改；如：startswith：表示以suffix开头，__contains__：包含suffix字符串
    return res_file_path if suffix == '' or suffix is None else list(filter(lambda x: x.endswith(suffix), res_file_path))



def analysisOneRunnerResult(result :str) -> int:
    print(result)


def analysisOneLogResult(result :str) -> int:
    pass

def analysisOneLogFile(filePath: str) -> list:

    f = open(filePath,'r',encoding='utf-8')
    fileLines = f.readlines()
    f.close()

    _keyword = "Finished-Acc"
    _pattern = re.compile(r'Finished-Acc:(0.[\d.]+)')

    accResult = []

    for idx, line in enumerate(fileLines):
        if _keyword not in line:
            continue
        
        ret = re.search(_pattern, line)

        if ret is None:
            continue
        
        accResult.append(ret[1])
    
    print(accResult)

    return accResult


def analysisOnePopLogFile(filePath: str) -> list:

    f = open(filePath,'r',encoding='utf-8')
    fileLines = f.readlines()
    f.close()

    # structurePattern = re.compile(r"indi:(\w+)\nAcc_mean:[-](\d+.\d+)\nAcc_std:[-](\d+.\d+)\nComplexity:(\d+)\n")
    structurePattern = re.compile(r"indi:(\w+)\sAcc_mean:[-]?(\d+.\d+)\sAcc_std:[-]?(\d+.\d+)\sComplexity:(\d+)\s")
    items = re.findall(structurePattern, "".join(fileLines))

    print(items)

    return [{
        "name": item[0],
        "complexity": item[3]
        } for item in items]




if __name__ == '__main__':

    popFiles = get_file("/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/aecnn_0317/populations", ".txt", [])

    popResults = []

    for filePath in popFiles:
        popName = ".".join(os.path.basename(filePath).split(".")[:-1])
        #print(fileName)
        onePopResult = analysisOnePopLogFile(filePath)

        popResults.append({
            "gen": popName,
            "result": onePopResult
        })
    
    # ret = analysisOnePopLogFile("/home/tuduweb/development/lightweight/ML-NAS/resources/evocnn_minst/populations/begin_00000.txt")
    # print(popResults)

    form_header = ['name', 'complexity']
    df = pd.DataFrame(columns=form_header)

    _pos = 0
    for idx, item in enumerate(popResults):
        for pidx, pitem in enumerate(item["result"]):
            df.loc[_pos + pidx] = [pitem["name"], pitem["complexity"]]
        _pos = _pos + len(item["result"])
        #df.loc[idx] = [item["name"], item["complexity"]]

    print(df)

    df.to_csv('result_pop.csv',index=False)
