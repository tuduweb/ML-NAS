import globalvar as gl

import deployer
import converter
from analysis import analysis_runnerLog

import os
import pandas as pd
from basicTools import fileTool


import argparse


def runModels_in_machine(models: 'str | list', inputSize:list = [1, 1, 28, 28], defaultMachine:str = "pi3", machine:object = None, piRunnerConfig2:map = {}) -> int:
    modelUrisList = []
    if isinstance(models, str):
        modelUrisList = fileTool.get_file(models, ".py", [])
    elif isinstance(models, list):
        modelUrisList = models

    # 将List内的文件转换成ncnnFiles
    res, results = converter.converModelsToNCCNFiles(
        modelUrisList,
        inputSize
    )

    if res < 0:
        return res

    # 这里可以采用多线程..

    # NCNN模型位置 ncnn.param
    modelsPath = ""
    if "modelsPath" in results.keys():
        modelsPath = results["modelsPath"]
    else:
        return -1

    piMachine = deployer.Pi3MachineConfig("172.16.72.144")
    piRunnerConfig = {
        "sources": modelsPath, # path or file
        "dest": os.path.join("/home/pi/lightweight/demo/", str(gl.get_value("start_time")) + "/" )
    }


    deployer.Machine_transfer_file_relative(piMachine, piRunnerConfig["sources"], piRunnerConfig["dest"])
    for item in results["finalResults"]:
        filename = item["name"] + ".ncnn.param"

        dstUri = os.path.join(os.path.join(piRunnerConfig["dest"], "ncnnModels"), filename)
        ret, result = deployer.Machine_exec_benchmark(piMachine, dstUri, args={})

        print("ret and result;", ret, result)

        if ret < 0:
            item["data"]["pitime"] = 999999
        else:
            timeRes = analysis_runnerLog.analysisOneRunnerResult(result)
            if timeRes == -1:
                timeRes = 999999
            item["data"]["pitime"] = timeRes


        item["data"]["x1time"] = 999999

        f = open("./runnerlog.txt", 'a+')
        _str = "%s=%s\n" % (filename, item["data"]["pitime"])
        f.write(_str)
        f.close()

    return results


def buildMap(mapKeys: str):
    pass


"""
input args: --source=path --sourcepath=/home/n504/onebinary/NAS-platform-runner-6682/runtime/p6579_fmnist_0430/scripts --machine=pi --hash=
h1682850573 --gen=0 --saveuri=/home/n504/onebinary/NAS-platform-runner-6682/runtime/p6579_fmnist_0430/runner/runner-00000.txt --mapuri=/home/n504/onebinary/NAS-platform-runner-6682/runtime/p6579_fmnist_0430/runner/map-00000.txt
"""
if __name__ == '__main__':
    gl.gl_init()

    # elif global_args.source == "path":
    parser = argparse.ArgumentParser(description='bin Neural Network pytorch Arch')
    parser.add_argument('--source', '-source', help='输入数据的来源', type=str, default="log")
    parser.add_argument('--sourcepath', '-sourcepath', help='输入数据的来源', type=str, default="")
    parser.add_argument('--coverlist', '-cl', help='输入数据的list', nargs='+')
    parser.add_argument('--hash', '-ha', help='此次结果文件哈希', type=str, default="none")
    parser.add_argument('--savepath', '-sp', help='结果存储地址', type=str, default="runnerLog/")
    parser.add_argument('--saveuri', '-su', help='结果存储详细地址', type=str, default="")
    parser.add_argument('--gen', '-gen', help='代目', type=int, default="")
    parser.add_argument('--machine', help='执行的机器', type=str, default="pi")
    parser.add_argument('--mapuri', help='文件和UUID的映射', type=str, default="")

    global_args = parser.parse_args()


    """
    程序正式过程..
    """

    # 获取所有的文件
    files = fileTool.get_file(global_args.sourcepath, ".py", [], keyword="indi%05d" % global_args.gen)

    results = runModels_in_machine(files, inputSize=[1, 1, 28, 28])

    # 构建结果
    form_header = ['name', 'gen', 'indi', 'macs', 'params', 'x1time', 'pitime']
    df = pd.DataFrame(columns=form_header)

    for idx, item in enumerate(results["finalResults"]):
        genAndIndi = item["name"].replace("indi", "").split("_")
        
        rowDatas = [item["name"], genAndIndi[0], genAndIndi[1]]
        rowDatas.append(item["data"]["macs"])
        rowDatas.append(item["data"]["params"])
        rowDatas.append(item["data"]["x1time"])
        rowDatas.append(item["data"]["pitime"])
        df.loc[idx] = rowDatas

    resultList = df[["name", "pitime"]].values.tolist()

    # convert 格式
    finalResult = {}

    for item in resultList:
        finalResult[item[0]] = item[1]

    print(df)