import globalvar as gl

import deployer
import converter
from analysis import analysis_runnerLog

import os
import pandas as pd
from basicTools import fileTool


import argparse


def buildRunner():
    pass

def runModel_in_machine(modelUri: str, inputSize = [1, 1, 32, 32]) -> int:
    res, macs, params, paramFileDstUri = converter.converModelToNCCNFiles(modelUri)

    if res < 0:
        return res

    x1eMachine = deployer.Binx1eMachineConfig()

    x1eRunnerConfig = {
        "sources": paramFileDstUri, # path or file
        "dest": "/home/tuduweb/development/demo/"
    }

    deployer.Machine_transfer_file_relative(x1eMachine, x1eRunnerConfig["sources"], x1eRunnerConfig["dest"])
    dstUri = os.path.join(x1eRunnerConfig["dest"], os.path.basename(paramFileDstUri))
    deployer.Machine_exec_benchmark(x1eMachine, dstUri, args={})


    piMachine = deployer.RaspMachineConfig("172.16.72.144")
    piRunnerConfig = {
        "sources": paramFileDstUri, # path or file
        "dest": "/home/pi/lightweight/demo/"
    }

    # deployer.Machine_transfer_file_relative(piMachine, piRunnerConfig["sources"], piRunnerConfig["dest"])
    # dstUri = os.path.join(piRunnerConfig["dest"], os.path.basename(paramFileDstUri))
    # deployer.Machine_exec_benchmark(piMachine, dstUri, args={})

def runModels_in_machine(models: 'str | list', inputSize = [1, 1, 28, 28]) -> int:

    modelUrisList = []

    if isinstance(models, str):
        # fileTool.get_file(models, ".py", [])
        #get files
        modelUrisList = fileTool.get_file(models, ".py", [])
    elif isinstance(models, list):
        modelUrisList = models

    res, results = converter.converModelsToNCCNFiles(
        modelUrisList,
        inputSize
    )

    if res < 0:
        return res

    x1eMachine = deployer.Binx1eMachineConfig()

    # NCNN模型位置 ncnn.param
    modelsPath = ""
    if "modelsPath" in results.keys():
        modelsPath = results["modelsPath"]
    else:
        return -1

    x1eRunnerConfig = {
        "sources": modelsPath, # path or file
        "dest": os.path.join("/home/tuduweb/development/demo/", str(gl.get_value("start_time")) + "/" )
    }

    """
    X1E Runner
    """

    # deployer.Machine_transfer_file_relative(x1eMachine, x1eRunnerConfig["sources"], x1eRunnerConfig["dest"])

    # for item in results["finalResults"]:
    #     filename = item["name"] + ".ncnn.param"

    #     dstUri = os.path.join(os.path.join(x1eRunnerConfig["dest"], "ncnnModels"), filename)
    #     ret, result = deployer.Machine_exec_benchmark(x1eMachine, dstUri, args={})
    
    #     print("ret and result;", ret, result)

    #     if ret < 0:
    #         item["data"]["x1time"] = 999999
    #     else:       
    #         timeRes = analysis_runnerLog.analysisOneRunnerResult(result)
    #         if timeRes == -1:
    #             timeRes = 999999
    #         item["data"]["x1time"] = timeRes


    """
    Raspberry Runner
    """

    piMachine = deployer.RaspMachineConfig("172.16.72.144")
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

        f = open("/home/n504/onebinary/NAS-platform-6679/runnerlog.txt", 'a+')
        _str = "%s=%s\n" % (filename, item["data"]["pitime"])
        f.write(_str)
        f.close()


    piMachine = deployer.RaspMachineConfig("172.16.72.144")
    piRunnerConfig = {
        "sources": modelsPath, # path or file
        "dest": "/home/pi/lightweight/demo/"
    }


    return results


from analysis import analysis_log

if __name__ == '__main__':
    gl.gl_init()

    parser = argparse.ArgumentParser(description='bin Neural Network pytorch Arch')
    parser.add_argument('--source', '-source', help='输入数据的来源', type=str, default="log")
    parser.add_argument('--sourcepath', '-sourcepath', help='输入数据的来源', type=str, default="")
    parser.add_argument('--coverlist', '-cl', help='输入数据的list', nargs='+')
    parser.add_argument('--hash', '-ha', help='此次结果文件哈希', type=str, default="none")
    parser.add_argument('--savepath', '-sp', help='结果存储地址', type=str, default="runnerLog/")
    parser.add_argument('--saveuri', '-su', help='结果存储详细地址', type=str, default="")
    parser.add_argument('--gen', '-gen', help='代目', type=int, default="")

    # parser.add_argument('--cuda', '-c', help='是否应用cuda', default=0)
    global_args = parser.parse_args()

    if global_args.source == "log":
        #anaysisLogReturnResults =[{'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00029.py', 'acc': 0.99067, 'rank': 1}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00043.py', 'acc': 0.99008, 'rank': 2}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00029_00016.py', 'acc': 0.98883, 'rank': 3}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00028.py', 'acc': 0.98775, 'rank': 4}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00001_00039.py', 'acc': 0.98742, 'rank': 5}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00034.py', 'acc': 0.98633, 'rank': 6}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00034_00002.py', 'acc': 0.98625, 'rank': 7}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00002_00040.py', 'acc': 0.98542, 'rank': 8}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00001_00019.py', 'acc': 0.98533, 'rank': 9}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00002_00043.py', 'acc': 0.98525, 'rank': 10}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00004.py', 'acc': 0.98492, 'rank': 11}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00002_00032.py', 'acc': 0.98483, 'rank': 12}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00006_00036.py', 'acc': 0.98442, 'rank': 13}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00003_00040.py', 'acc': 0.98308, 'rank': 14}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00003_00044.py', 'acc': 0.9825, 'rank': 15}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00033_00027.py', 'acc': 0.98233, 'rank': 16}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00023.py', 'acc': 0.98233, 'rank': 17}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00001_00048.py', 'acc': 0.982, 'rank': 18}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00009_00047.py', 'acc': 0.98117, 'rank': 19}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review/scripts/indi00000_00040.py', 'acc': 0.981, 'rank': 20}]
        anaysisLogReturnResults = analysis_log.main('/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review5_36', 20)
        runModelsUriList = []
        for resultItem in anaysisLogReturnResults:
            runModelsUriList.append(resultItem['scriptUri'])

        print(runModelsUriList)

        # runModelsUriList = ["indi00009_00002.py"]

        """
        执行区域
        """

        results = runModels_in_machine(runModelsUriList)

        #results = {'modelsPath': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/./outputs/1679218920/ncnnModels/', 'finalResults': [{'name': 'indi00000_00029', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00029.ncnn.param', 'data': {'macs': 23605782.0, 'params': 3337615.0, 'x1time': 2.902}}, {'name': 'indi00000_00043', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00043.ncnn.param', 'data': {'macs': 12093968.0, 'params': 179676.0, 'x1time': 0.661}}, {'name': 'indi00029_00016', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00029_00016.ncnn.param', 'data': {'macs': 4542328.0, 'params': 49353.0, 'x1time': 0.329}}, {'name': 'indi00000_00028', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00028.ncnn.param', 'data': {'macs': 222938736.0, 'params': 4061807.0, 'x1time': 7.0875}}, {'name': 'indi00001_00039', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00001_00039.ncnn.param', 'data': {'macs': 3088062.0, 'params': 67698.0, 'x1time': 0.33}}, {'name': 'indi00000_00034', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00034.ncnn.param', 'data': {'macs': 34757650.0, 'params': 4362777.0, 'x1time': 3.982}}, {'name': 'indi00034_00002', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00034_00002.ncnn.param', 'data': {'macs': 4203984.0, 'params': 33259.0, 'x1time': 0.306}}, {'name': 'indi00002_00040', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00002_00040.ncnn.param', 'data': {'macs': 2646934.0, 'params': 22419.0, 'x1time': 0.2625}}, {'name': 'indi00001_00019', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00001_00019.ncnn.param', 'data': {'macs': 136531876.0, 'params': 296142.0, 'x1time': 4.222}}, {'name': 'indi00002_00043', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00002_00043.ncnn.param', 'data': {'macs': 4737626.0, 'params': 94001.0, 'x1time': 0.406}}, {'name': 'indi00000_00004', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00004.ncnn.param', 'data': {'macs': 9639848.0, 'params': 2869745.0, 'x1time': 999999}}, {'name': 'indi00002_00032', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00002_00032.ncnn.param', 'data': {'macs': 105562808.0, 'params': 584361.0, 'x1time': 4.257}}, {'name': 'indi00006_00036', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00006_00036.ncnn.param', 'data': {'macs': 4368904.0, 'params': 297642.0, 'x1time': 0.442}}, {'name': 'indi00003_00040', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00003_00040.ncnn.param', 'data': {'macs': 62155910.0, 'params': 314516.0, 'x1time': 2.452}}, {'name': 'indi00003_00044', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00003_00044.ncnn.param', 'data': {'macs': 3785290.0, 'params': 110414.0, 'x1time': 0.804}}, {'name': 'indi00033_00027', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00033_00027.ncnn.param', 'data': {'macs': 8565100.0, 'params': 14688.0, 'x1time': 0.3545}}, {'name': 'indi00000_00023', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00023.ncnn.param', 'data': {'macs': 182657011.0, 'params': 4974225.0, 'x1time': 4.218}}, {'name': 'indi00001_00048', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00001_00048.ncnn.param', 'data': {'macs': 14089430.0, 'params': 457661.0, 'x1time': 0.659}}, {'name': 'indi00009_00047', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00009_00047.ncnn.param', 'data': {'macs': 18936146.0, 'params': 192618.0, 'x1time': 999999}}, {'name': 'indi00000_00040', 'dstUri': '/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679218920/ncnnModels/indi00000_00040.ncnn.param', 'data': {'macs': 6942392.0, 'params': 367442.0, 'x1time': 0.497}}]}

        """
        数据生成区域
        """

        formatResults = {}


        # TODO: data merge program

        for item in results["finalResults"]:
            print(item["name"])
            formatResults[item["name"]] = item["data"]
            print(item["data"])
        form_header = ['name', 'gen', 'indi', 'acc', 'macs', 'params', 'x1time', 'pitime']
        df = pd.DataFrame(columns=form_header)

        if anaysisLogReturnResults:
            for idx, item in enumerate(anaysisLogReturnResults):
                itemName = os.path.basename(item["scriptUri"]).replace(".py", "")
                genAndIndi = itemName.replace("indi", "").split("_")
                
                rowDatas = [itemName, None, None, item["acc"]]


                if len(genAndIndi) == 2:
                    rowDatas[1] = genAndIndi[0]
                    rowDatas[2] = genAndIndi[1]
                else:
                    rowDatas[1] = -1
                    rowDatas[2] = -1
                
                if itemName in formatResults.keys():
                    rowDatas.append(formatResults[itemName]["macs"])
                    rowDatas.append(formatResults[itemName]["params"])
                    rowDatas.append(formatResults[itemName]["x1time"])
                    rowDatas.append(formatResults[itemName]["pitime"])
                
                df.loc[idx] = rowDatas
        
        print(df)

        df.to_csv('runner_%d.csv' % gl.get_value("start_time"), index=False)


    elif global_args.source == "list":
        print(global_args.coverlist)
        exit(0)
        results = runModels_in_machine(global_args.coverlist)
        print(results)
    elif global_args.source == "path":
        """
        这里供系统使用中..
        """
        #files = fileTool.get_file("~/onebinary/MO_MNIST_0.3loss", ".py", [])
        files = fileTool.get_file(global_args.sourcepath, ".py", [], keyword="indi%05d" % global_args.gen)

        # input_size = [1, 3, 32, 32]

        print("files", files)

        results = runModels_in_machine(files, inputSize=[1, 3, 32, 32])
        # results = runModels_in_machine(files, inputSize=[1, 1, 28, 28])

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


        # print(df)

        #print(df[["name", "pitime"]].values.tolist())

        resultList = df[["name", "pitime"]].values.tolist()

        # convert 格式
        finalResult = {}

        for item in resultList:
            finalResult[item[0]] = item[1]


        file_name = global_args.saveuri
        if file_name == "":
            file_name = '%s/runner_result.txt' % (os.path.join(global_args.savepath, 'demo'))
        
        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        # df.to_csv(os.path.join(gl.get_value("pwd"), 'runner_tmpsave_%d.csv' % gl.get_value("start_time")), index=False)


        f = open(file_name, 'a+')
        _str = "%s=%s\n" % (global_args.hash, str(finalResult))
        f.write(_str)
        f.close()

        # print(results["finalResults"])

    elif global_args.source == "hand":
        files = fileTool.get_file("~/onebinary/MO_MNIST_0.3loss", ".py", [])
        print("files", files)

        results = runModels_in_machine(files, inputSize=[1, 3, 32, 32])

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


        # print(df)

        #print(df[["name", "pitime"]].values.tolist())

        resultList = df[["name", "pitime"]].values.tolist()

        # convert 格式
        finalResult = {}

        for item in resultList:
            finalResult[item[0]] = item[1]


        print(df)

        # df.to_csv(os.path.join(gl.get_value("pwd"), 'runner_tmpsave_%d.csv' % gl.get_value("start_time")), index=False)
