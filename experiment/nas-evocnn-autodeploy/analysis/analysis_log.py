import os
import sys
import csv
import re
import pandas as pd

class RunnerAnalysis(object):
    pass


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

def analysisOneLogFile(filePath: str, isSearchEpoch: bool = True) -> tuple:

    f = open(filePath,'r',encoding='utf-8')
    fileLines = f.readlines()
    f.close()

    segs = []

    _startLine = -1
    _endLine = -1

    _startKeywords = "Used "
    _endKeywords = "Finished-Acc"
    _pattern = re.compile(r'Finished-Acc:(0.[\d.]+)')

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

    _epochPattern = re.compile(r'\[(.+)\]-(\w+)-Epoch:\s*(\d+),\s*(.*)')

    epochResults = []

    for segId, (_s, _e) in enumerate(segs):
        _epochResult = []
        for idx, line in enumerate(fileLines[_s: _e + 1]):

            if _endKeywords in line:    
                ret = re.search(_pattern, line)

                if ret is None:
                    continue
                
                accResult.append(ret[1])
        
            elif isSearchEpoch:
                ret = re.search(_epochPattern, line)
                if ret is None:
                    continue
                
                # time, type, round, logs
                rets = (ret[1], ret[2], ret[3], ret[4])

                _epochResult.append(rets)

        if isSearchEpoch:
            epochResults.append(_epochResult)

    print(accResult)
    print(epochResults)

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

if __name__ == '__main__':

    isAnalysisRemote = True

    # ana
    if isAnalysisRemote:
        # scp -P 22 n504@lab-3090-3:~/.. ~/..
        # Method 1: 从远端获取文件.. 再使用本地的方式
        # remote_cmd = 'sshpass -p {ssh_passwd} ssh {ssh_name}@{worker_ip} -p {port} kill -TERM -- -{PID}'.format(
        #     ssh_name = ssh_name,
        #     ssh_passwd = ssh_passwd,
        #     worker_ip = worker_ip,
        #     port = ssh_port,
        #     PID = worker_pid
        # )

        # _, std_err = exec_cmd_remote(remote_cmd, need_response=True)
        pass

    filesPath = "/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/aecnn_0317/log"
    files = get_file(filesPath, ".txt", [])
    print("files[%s] num: %d" % (filesPath, len(files)))

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

        break


    form_header = ['name', 'acc', 'accResults']
    df = pd.DataFrame(columns=form_header)

    for idx, item in enumerate(logParsedResult):
        df.loc[idx] = [item["name"], item["acc"], item["accResults"]]
        print(item)

    df[["acc"]] = df[["acc"]].apply(pd.to_numeric)
    df.sort_values("acc", inplace=True, ascending=False)

    print(df)

    # df.to_csv('result2.csv',index=False)


    #print(df["name"].iloc[ 0: 20, ].values.tolist())
    print(df[["name", "acc"]].iloc[ 0: 20, ].values.tolist())

    # 取得Top的一些数据