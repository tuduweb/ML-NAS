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

from models import indi00000_00002
#from models import indi00031_00028


parser = argparse.ArgumentParser(description='bin Neural Network pytorch Arch')
parser.add_argument('--cuda', '-c', help='是否应用cuda', default=0)
global_args = parser.parse_args()

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

def pathCoverToLib(file_path: str) -> str:
    #file_path.
    base_name = os.path.splitext(file_path)[0]

    # TODO: 去掉相对路径的起始 ./
    print(base_name)

    return ".".join(base_name.split("/"))

    pass


def execPnnx(script_path: str) -> int:
    pass

if __name__ == '__main__':

    # 初始化
    gl.set_value("pwd", sys.path[0])
    gl.set_value("cur_time", int(time.time()))


    # 读取指定文件夹下所有的东西
    files = get_file("models/temp/", ".py", [])

    i = 0

    batch_size = 1  # 批处理大小
    #input_shape = (3, 32, 32)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸
    input_shape = (1, 28, 28)  # 输入数据,我这里是灰度训练所以1代表是单通道，RGB训练是3，128是图像输入网络的尺寸
    # 生成张量
    x = torch.randn(batch_size, *input_shape).cpu()

    # 保存地址
    savePath = os.path.join(gl.get_value("pwd"), "./outputs/", str(gl.get_value("cur_time")))

    modelsPath = os.path.join(savePath, "ncnnModels/")
    os.makedirs(modelsPath)

    for file in files:
        
        if i == 100:
            exit(0)

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

        pnnxExec = "/home/tuduweb/Downloads/pnnx-20230227-ubuntu/pnnx"

        # ret = os.system("/home/n504/Downloads/pnnx-20221116-ubuntu/pnnx " + savedFileUri + " inputshape=[1,3,32,32]")
        ret = os.system(pnnxExec + " " + savedFileUri + " inputshape=[1,1,28,28]")
        print("program result: %d" % ret)

        paramFileSrcUri = os.path.abspath(os.path.join(os.path.dirname(savedFileUri), "./model.ncnn.param"))
        paramFileDstUri = os.path.abspath(os.path.join(modelsPath, fileName + ".ncnn.param"))
        ret = os.system("cp " + paramFileSrcUri + " " + paramFileDstUri)


        print("cp result: %d" % ret)

        i = i + 1
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