from torchsummary import summary
import torch
from thop import profile
from thop import clever_format

import os
import sys
import time

import globalvar as gl

import importlib
import argparse

from basicTools import fileTool

parser = argparse.ArgumentParser(description='bin Neural Network pytorch Arch')
parser.add_argument('--cuda', '-c', help='是否应用cuda', default=0)
global_args = parser.parse_args()


def pathCoverToLib(file_path: str) -> str:
    #file_path.
    base_name = os.path.splitext(file_path)[0]

    # TODO: 去掉相对路径的起始 ./
    #print(base_name)

    return ".".join(base_name.split("/"))

    pass


"""
    Pnnx Tools
"""

def execPnnxConverter(savedFileUri: str, inputShape: str = "[1,3,32,32]") -> int:
    """
    cover PnnxScript to NCNN files
    """

    pnnxExec = "/home/n504/onebinary/pnnx-20230227-ubuntu/pnnx"

    # ret = os.system("/home/n504/Downloads/pnnx-20221116-ubuntu/pnnx " + savedFileUri + " inputshape=[1,3,32,32]")
    ret = os.system(pnnxExec + " " + savedFileUri + " inputshape=" + inputShape.strip())
    print("program result: %d" % ret)

    return ret


def converModelToNCCNFiles(modelPath: str, modelInputShape=[1, 1, 28, 28]):

    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("start_time")))
    modelsPath = os.path.join(savePath, "ncnnModels/")
    pnnxExecUri = "/home/n504/onebinary/pnnx-20230227-ubuntu/pnnx"

    # gl.set_value("cur_time", int(time.time()))
    
    # 输出值
    macs = ""
    params = ""
    paramFileDstUri = ""

    for file in [modelPath]:
        # TODO: 更合理的引入逻辑
        libName = pathCoverToLib(file)
        indiLib = importlib.import_module(libName)

        fileName = libName.split(".")[-1]

        try:
            model = indiLib.EvoCNNModel()
            model.eval().cpu()
            
            # print(model)


            x = torch.randn(modelInputShape).cpu()

            macs, params = profile(model, inputs=(x, ))
            # macs, params = clever_format([macs, params], "%.3f")

            print("macs %s ; params %s." % clever_format([macs, params], "%.3f"))
        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue
        

        try:
            curPath = os.path.join(savePath, fileName)
            os.makedirs(curPath)

            savedFileName = "./model.pth"
            savedFileUri = os.path.join(curPath, savedFileName)

            # 转换成TorchScript
            mod = torch.jit.trace(model, x)
            mod.save(savedFileUri)

            inputshapeStr = ",".join(str(item) for item in modelInputShape)
            print("inputshape", inputshapeStr)
            ret = os.system(pnnxExecUri + " " + savedFileUri + " inputshape=[" + inputshapeStr + "]")
            print("program result: %d" % ret)

            paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
            paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))

            if not os.path.exists(modelsPath):
                os.makedirs(modelsPath)

            ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)

            print("cp result: %d" % ret)

        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue

    return 0, macs, params, paramFileDstUri


def converModelsToNCCNFiles(modelUriLists: list, modelInputShape=[1, 1, 28, 28]):

    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("start_time")))
    modelsPath = os.path.join(savePath, "ncnnModels/")
    pnnxExecUri = "/home/n504/onebinary/pnnx-20230227-ubuntu/pnnx"

    # gl.set_value("cur_time", int(time.time()))
    
    coverdLists = []

    tmpModelsPath = os.path.join(gl.get_value("pwd"), "models", "t" + str(gl.get_value("start_time")))
    if not os.path.exists(tmpModelsPath):
        os.makedirs(tmpModelsPath)

    for modelUri in modelUriLists:
        if not os.path.exists(modelUri):
            continue

        modelFileName = os.path.basename(modelUri)
        ret = os.system("cp " + modelUri + " " + tmpModelsPath)
        print("cp result: %d" % ret)

        tmpModelUri = os.path.realpath(os.path.join(tmpModelsPath, modelFileName))
        _pwd = os.path.realpath(gl.get_value("pwd"))

        if tmpModelUri.startswith(_pwd):
            tmpModelUri = tmpModelUri.replace(_pwd + "/", "")
    
        coverdLists.append(tmpModelUri)

    importlib.invalidate_caches()

    finalResults = []

    for tmpModelUri in coverdLists:

        libName = pathCoverToLib(tmpModelUri)
        indiLib = importlib.import_module(libName)

        fileName = libName.split(".")[-1]

        try:
            model = indiLib.EvoCNNModel()
            model.eval().cpu()

            x = torch.randn(modelInputShape).cpu()

            macs, params = profile(model, inputs=(x, ))
            # macs, params = clever_format([macs, params], "%.3f")

            print("macs %s ; params %s." % clever_format([macs, params], "%.3f"))

            # convert
            curPath = os.path.join(savePath, fileName)
            os.makedirs(curPath)

            savedFileName = "./model.pth"
            savedFileUri = os.path.join(curPath, savedFileName)

            # 转换成TorchScript
            mod = torch.jit.trace(model, x)
            mod.save(savedFileUri)

            savedFileUri = os.path.realpath(savedFileUri)


            inputshapeStr = ",".join(str(item) for item in modelInputShape)
            ret = os.system(pnnxExecUri + " " + savedFileUri + " inputshape=[" + inputshapeStr + "]")
            print("program result: %d" % ret)

            paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
            paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))

            if not os.path.exists(modelsPath):
                os.makedirs(modelsPath)

            ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)

            print("cp result: %d" % ret)

            if ret == 0:
                finalResults.append({
                    "name": fileName,
                    "dstUri": paramFileDstUri,
                    "data": {
                        "macs": macs,
                        "params": params
                    }
                })


        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue

    print("finalResults", finalResults)

    return 0, {
        "modelsPath": modelsPath,
        "finalResults": finalResults
    }

    # 输出值
    macs = ""
    params = ""
    paramFileDstUri = ""

    for file in modelUriLists:
        # TODO: 更合理的引入逻辑
        libName = pathCoverToLib(file)
        indiLib = importlib.import_module(libName)

        fileName = libName.split(".")[-1]

        try:
            model = indiLib.EvoCNNModel()
            model.eval().cpu()
            
            # print(model)


            x = torch.randn(modelInputShape).cpu()

            macs, params = profile(model, inputs=(x, ))
            # macs, params = clever_format([macs, params], "%.3f")

            print("macs %s ; params %s." % clever_format([macs, params], "%.3f"))
        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue
        

        try:
            curPath = os.path.join(savePath, fileName)
            os.makedirs(curPath)

            savedFileName = "./model.pth"
            savedFileUri = os.path.join(curPath, savedFileName)

            # 转换成TorchScript
            mod = torch.jit.trace(model, x)
            mod.save(savedFileUri)

            inputshapeStr = ",".join(str(item) for item in modelInputShape)
            print("inputshape", inputshapeStr)
            ret = os.system(pnnxExecUri + " " + savedFileUri + " inputshape=[" + inputshapeStr + "]")
            print("program result: %d" % ret)

            paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
            paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))

            if not os.path.exists(modelsPath):
                os.makedirs(modelsPath)

            ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)

            print("cp result: %d" % ret)

        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue

    return 0, macs, params, paramFileDstUri


def execPnnxFile(script_path: str) -> int:

    pass


def modelNamesToFileAndCopyToPwd(modelNames: str) -> int:
    pass


def main():
    gl.set_value("pwd", sys.path[0])
    gl.set_value("cur_time", int(time.time()))

    files = []
    # resultsFromAnalaysisLog = [{'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00009_00002.py', 'acc': 0.99383, 'rank': 1}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00006_00009.py', 'acc': 0.99375, 'rank': 2}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00008_00003.py', 'acc': 0.99375, 'rank': 3}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00006_00006.py', 'acc': 0.99358, 'rank': 4}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00006_00012.py', 'acc': 0.99358, 'rank': 5}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00010_00003.py', 'acc': 0.99358, 'rank': 6}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00005_00011.py', 'acc': 0.99358, 'rank': 7}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00009_00004.py', 'acc': 0.99358, 'rank': 8}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00007_00011.py', 'acc': 0.99342, 'rank': 9}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00009_00003.py', 'acc': 0.99342, 'rank': 10}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00010_00004.py', 'acc': 0.99342, 'rank': 11}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00007_00006.py', 'acc': 0.99333, 'rank': 12}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00007_00004.py', 'acc': 0.99333, 'rank': 13}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00006_00003.py', 'acc': 0.99333, 'rank': 14}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00004_00011.py', 'acc': 0.99325, 'rank': 15}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00008_00010.py', 'acc': 0.99325, 'rank': 16}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00009_00007.py', 'acc': 0.99317, 'rank': 17}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00004_00014.py', 'acc': 0.99317, 'rank': 18}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00006_00008.py', 'acc': 0.99317, 'rank': 19}, {'scriptUri': '/home/n504/onebinary/ENAS_6379/runtime/pso_MNIST_review3/scripts/indi00007_00009.py', 'acc': 0.99308, 'rank': 20}]
    
    # tmpModelDir = os.path.join(gl.get_value("pwd"), "./models/", str(gl.get_value("cur_time")))
    # os.makedirs(tmpModelDir)

    # for resultItem in resultsFromAnalaysisLog:
    #     targetUri = os.path.join("models/", str(gl.get_value("cur_time")), os.path.basename(resultItem["scriptUri"]))
    #     dstModelUri = os.path.realpath(targetUri)
    #     ret = os.system("cp " + resultItem["scriptUri"] + " " + dstModelUri)
    #     if ret == 0:
    #         files.append(targetUri)


    files = ["indi00000_00029.py"]
    pnnxExec = "/home/n504/onebinary/pnnx-20230227-ubuntu/pnnx"

    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("cur_time")))
    modelsPath = os.path.join(savePath, "ncnnModels/")
    os.makedirs(modelsPath)


    # x = torch.randn([1, 3, 32, 32]).cpu()
    x = torch.randn([1, 1, 28, 28]).cpu()
    #input_shape = (1, 28, 28)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸

    for file in files:
        libName = pathCoverToLib(file)
        indiLib = importlib.import_module(libName)

        fileName = libName.split(".")[-1]

        try:
            model = indiLib.EvoCNNModel()

            model.eval().cpu()
            
            print(model)

            macs, params = profile(model, inputs=(x, ))
            macs, params = clever_format([macs, params], "%.3f")

            print("macs %s ; params %s." % (macs, params))
        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue

        curPath = os.path.join(savePath, fileName)
        os.makedirs(curPath)

        savedFileName = "./model.pth"
        savedFileUri = os.path.join(curPath, savedFileName)

        # 转换成TorchScript
        mod = torch.jit.trace(model, x)
        mod.save(savedFileUri)

        # ret = os.system("/home/n504/Downloads/pnnx-20221116-ubuntu/pnnx " + savedFileUri + " inputshape=[1,3,32,32]")
        ret = os.system(pnnxExec + " " + savedFileUri + " inputshape=[1,1,28,28]")
        print("program result: %d" % ret)

        paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
        paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))
        ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)


        print("cp result: %d" % ret)

        break

if __name__ == '__main__':

    main()
    exit()

    # 初始化
    gl.set_value("pwd", sys.path[0])
    gl.set_value("cur_time", int(time.time()))


    # 读取指定文件夹下所有的东西
    #files = fileTool.get_file("models/temp/", ".py", [])
    files = ["indi00000_00007.py"]

    batch_size = 1  # 批处理大小
    input_shape = (3, 32, 32)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸
    #input_shape = (1, 28, 28)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸
    # 生成张量
    x = torch.randn(batch_size, *input_shape).cpu()

    # 保存地址
    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("cur_time")))

    modelsPath = os.path.join(savePath, "ncnnModels/")
    os.makedirs(modelsPath)

    for file in files:
        libName = pathCoverToLib(file)
        indiLib = importlib.import_module(libName)

        fileName = libName.split(".")[-1]
        # print(fileName)

        try:
            model = indiLib.EvoCNNModel()

            model.eval().cpu()
            
            print(model)

            macs, params = profile(model, inputs=(x, ))
            macs, params = clever_format([macs, params], "%.3f")

            print("macs %s ; params %s." % (macs, params))
        except RuntimeError as e:
            print("发生错误", e)
            continue
        except ZeroDivisionError as e:
            print("发生错误 ZeroDivisionError", e)
            continue
        except Exception as e:
            print("发生其它错误", e)
            continue

        curPath = os.path.join(savePath, fileName)
        os.makedirs(curPath)

        savedFileName = "./model.pth"
        savedFileUri = os.path.join(curPath, savedFileName)

        # 转换成TorchScript
        mod = torch.jit.trace(model, x)
        mod.save(savedFileUri)

        pnnxExec = "/home/n504/onebinary/pnnx-20230227-ubuntu/pnnx"

        # ret = os.system("/home/n504/Downloads/pnnx-20221116-ubuntu/pnnx " + savedFileUri + " inputshape=[1,3,32,32]")
        ret = os.system(pnnxExec + " " + savedFileUri + " inputshape=[1,3,32,32]")
        print("program result: %d" % ret)

        paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
        paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))
        ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)


        print("cp result: %d" % ret)
    exit(0)

    indiModel = importlib.import_module('models.indi00000_00002')

    filename = "indi00000_00002"

    model = indi00000_00002.EvoCNNModel()
    
    # # params summary & others
    #summary(model.cuda(), (3, 32, 32), batch_size=1)

    # # 是否需要读取模型参数?
    # model.load_state_dict(torch.load('./model/indi00031_00028.pt'), False)  # 加载训练好的pth模型

    model.eval().cpu()  # cpu推理

    batch_size = 1  # 批处理大小
    input_shape = (3, 32, 32)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸
    # 生成张量
    x = torch.randn(batch_size, *input_shape).cpu()

    macs, params = profile(model, inputs=(x, ))
    macs, params = clever_format([macs, params], "%.3f")


    # 保存地址
    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("cur_time")))

    curPath = os.path.join(savePath, filename)
    os.makedirs(curPath)

    savedFileName = "./model.pth"
    savedFileUri = os.path.join(curPath, savedFileName)

    # 转换成TorchScript
    mod = torch.jit.trace(model, x)
    mod.save(savedFileUri)

    # 转换成ncnn相关的文件
    

    ret = os.system("/home/n504/Downloads/pnnx-20221116-ubuntu/pnnx " + savedFileUri + " inputshape=[1,3,32,32]")
    print("program result: %d" % ret)
    # 判断.param可行性，即检查算子是否完全支持等


    # 传输到实机判别



    # 输出结果
    print("macs %s ; params %s." % (macs, params))