import os
import sys
import csv
import re
import pandas as pd

class RunnerAnalysis(object):
    pass


def get_file(file_path: str, suffix: str, res_file_path: list, keyword: str = "") -> list:
    """获取路径下的指定文件类型后缀的文件

    Args:
        file_path: 文件夹的路径
        suffix: 要提取的文件类型的后缀
        res_file_path: 保存返回结果的列表

    Returns: 文件路径

    """

    for file in os.listdir(file_path):

        if os.path.isdir(os.path.join(file_path, file)):
            get_file(os.path.join(file_path, file), suffix, res_file_path, keyword=keyword)
        else:
            if keyword != '' and keyword in file:
                continue
            res_file_path.append(os.path.join(file_path, file))

    # endswith：表示以suffix结尾。可根据需要自行修改；如：startswith：表示以suffix开头，__contains__：包含suffix字符串
    return res_file_path if suffix == '' or suffix is None else list(filter(lambda x: x.endswith(suffix), res_file_path))



def analysisOneRunnerResult(result :str) -> int:
    print(result)


def analysisOneLogResult(result :str) -> int:
    pass

def analysisOneLogFile(filePath: str, isSearchEpoch: bool = True, endKeyword = "Finished-Error") -> tuple:
    """
    endKeyword = "Finished-Acc"
    endKeyword = "Finished-Error"
    """

    isEndError = True if endKeyword == "Finished-Error" else False

    f = open(filePath,'r',encoding='utf-8')
    fileLines = f.readlines()
    f.close()

    segs = []

    _startLine = -1
    _endLine = -1

    _startKeywords = "Used "
    _endKeywords = endKeyword
    _pattern = re.compile(endKeyword + r':(0.[\d.]+)')

    for idx, line in enumerate(fileLines):
        # drop no end data
        if _startKeywords in line:
            _startLine = idx
        
        if _startLine >= 0 and _endKeywords in line:
            _endLine = idx

        if _startLine >= 0 and _endLine > _startLine:
            segs.append((_startLine, _endLine))
            _startLine = _endLine = -1



    accResult = []

    """
    [2023-03-17 12:36:20.075108]-Train-Epoch:  1,  Loss: 1.683, Acc:0.377
    [2023-03-17 12:36:22.275163]-Valid-Epoch:  1, Loss:1.972, Acc:0.356
    [2023-03-17 12:36:39.264636]-Train-Epoch:  2,  Loss: 1.427, Acc:0.481
    [2023-03-17 12:36:41.382842]-Valid-Epoch:  2, Loss:1.668, Acc:0.432
    """

    """
    [2023-03-18 16:23:19.759561]-Valid-Epoch:  8, Loss:0.19160, Acc:0.95225
    [2023-03-18 16:24:17.845441]-Train-Epoch:  9,  Loss: 0.28218, Acc:0.91894
    [2023-03-18 16:24:27.807154]-Valid-Epoch:  9, Loss:0.20471, Acc:0.94417
    [2023-03-18 16:25:09.543063]-Train-Epoch: 10,  Loss: 0.27824, Acc:0.91923
    [2023-03-18 16:25:16.874860]-Valid-Epoch: 10, Loss:0.19239, Acc:0.94617
    [2023-03-18 16:25:16.876941]-Finished-Error:0.04775, num-para:1430447
    """

    _epochPattern = re.compile(r'\[(.+)\]-(\w+)-Epoch:\s*(\d+),\s*(.*)')

    epochResults = []

    for segId, (_s, _e) in enumerate(segs):
        _epochResult = []
        for idx, line in enumerate(fileLines[_s: _e + 1]):

            if _endKeywords in line:    
                ret = re.search(_pattern, line)

                if ret is None:
                    continue
                
                res = float(ret[1])
                if isEndError:
                    res = 1.0 - res
                accResult.append(res)
        
            elif isSearchEpoch:
                ret = re.search(_epochPattern, line)
                if ret is None:
                    continue
                
                # time, type, round, logs
                rets = (ret[1], ret[2], ret[3], ret[4])

                _epochResult.append(rets)

        if isSearchEpoch:
            epochResults.append(_epochResult)

    return accResult, epochResults

def analysisOneLogFile_AccResult(filePath: str) -> list:
    return analysisOneLogFile(filePath = filePath, isSearchEpoch = False)[0]



import subprocess
import selectors

def exec_cmd_remote(_cmd, need_response=True):
    p = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_str = None
    stderr_str = None

    if need_response:
        sel = selectors.DefaultSelector()
        sel.register(p.stdout, selectors.EVENT_READ)
        sel.register(p.stderr, selectors.EVENT_READ)
        stdout_ = None
        stderr_ = None
        for key, _ in sel.select():
            data = key.fileobj.readlines()

            if key.fileobj is p.stdout:
                stdout_ = data
            else:
                stderr_ = data

        if stdout_ is not None and len(stdout_) > 0:
            stdout_str = ''.join([_.decode('utf-8') for _ in stdout_])

        if stderr_ is not None and len(stderr_) > 0:
            stderr_str = ''.join([_.decode('utf-8') for _ in stderr_])

    return stdout_str, stderr_str


def analysis_log_for_files(logFilesPath: str) -> list:

    files = get_file(logFilesPath, ".txt", [])
    print("analysis path: %s" % logFilesPath)

    logParsedResult = []

    for filePath in files:
        fileName = ".".join(os.path.basename(filePath).split(".")[:-1])
        #print(fileName)
        accResults = analysisOneLogFile_AccResult(filePath)

        logParsedResult.append({
            "name": fileName,
            "accResults": accResults,
            "acc": max(accResults) if len(accResults) != 0 else 0
        })

    return logParsedResult


# def make_logs_group(results: list) -> int:
#     for item in results:
#         print(item[0])
#     pass

def analysis_trainLog_for_files(logFilesPath: str) -> map:

    files = get_file(logFilesPath, ".txt", [])
    print("analysis path: %s" % logFilesPath)

    logParsedResult = {}

    for filePath in files:
        fileName = ".".join(os.path.basename(filePath).split(".")[:-1])
        #print(fileName)
        _, oneTrainLog = analysisOneLogFile(filePath)

        if len(oneTrainLog) == 0:
            print("%s empty" % filePath)
        else:
            print(oneTrainLog)
        logParsedResult[fileName] = oneTrainLog

    return logParsedResult

def main(filesPath: str = "/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review", maxReturnNum: int = 20) -> list:

    paths = {
        "logPath": os.path.realpath(os.path.join(filesPath, "log")),
        "scriptPath": os.path.realpath(os.path.join(filesPath, "scripts")),
    }

    files = get_file(paths["logPath"], ".txt", [])
    print("files[%s] num: %d" % (paths["logPath"], len(files)))

    logParsedResult = []

    logGenAndIndiResult = {}
    isGenerateGenAndIndiResult = False

    isGenerate_trainResult = False

    for filePath in files:
        fileName = ".".join(os.path.basename(filePath).split(".")[:-1])
        #print(fileName)
        #accResults = analysisOneLogFile_AccResult(filePath)

        accResults, trainLogs = analysisOneLogFile(filePath = filePath, isSearchEpoch = isGenerate_trainResult)

        logParsedResult.append({
            "name": fileName,
            "accResults": accResults,
            "acc": max(accResults) if len(accResults) != 0 else 0
        })


        # Generate GenAndIndi Result
        if isGenerateGenAndIndiResult:
            genAndIndi = fileName.replace('indi', '').split('_')
            if len(genAndIndi) != 2:
                continue

            gen = genAndIndi[0]
            indi = genAndIndi[1]
            if gen not in logGenAndIndiResult.keys():
                logGenAndIndiResult[gen] = {}

            logGenAndIndiResult[gen][indi] = {
                "acc": max(accResults) if len(accResults) != 0 else 0,
                "accResults": accResults
            }

        # trainLog
        if isGenerate_trainResult:
            for trainLog in trainLogs:
                for log in trainLog:
                    print(log)

    form_header = ['name', 'gen', 'indi', 'acc', 'accResults']
    df = pd.DataFrame(columns=form_header)

    for idx, item in enumerate(logParsedResult):
        genAndIndi = item["name"].replace("indi", "").split("_")
        if len(genAndIndi) == 2:
            df.loc[idx] = [item["name"], genAndIndi[0], genAndIndi[1], item["acc"], item["accResults"]]
        else:
            df.loc[idx] = [item["name"], "-1", "-1", item["acc"], item["accResults"]]

    df[["acc"]] = df[["acc"]].apply(pd.to_numeric)
    df.sort_values("acc", inplace=True, ascending=False)

    print(df)

    df.to_csv('result3.csv',index=False)


    #print(df["name"].iloc[ 0: 20, ].values.tolist())
    #print(df[["name", "acc"]].iloc[ 0: 20, ].values.tolist())

    # 取得Top的一些数据
    _length = len(df)
    filterList = []
    if maxReturnNum == -1 or maxReturnNum >= _length:
        filterList = df[["name", "acc"]].values.tolist()
    else:
        filterList = df[["name", "acc"]].iloc[ 0: maxReturnNum, ].values.tolist()
    
    
    returnList = []

    for idx, item in enumerate(filterList):
        scriptUri = os.path.realpath(os.path.join(paths["scriptPath"], item[0] + ".py"))

        if not os.path.exists(scriptUri):
            continue

        returnList.append({
            "scriptUri": scriptUri,
            "acc": item[1],
            "rank": idx + 1
        })

    print("log.main return", returnList)
    return returnList

if __name__ == '__main__':
    main()