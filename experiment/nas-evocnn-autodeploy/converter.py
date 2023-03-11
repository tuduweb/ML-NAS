from torchsummary import summary
import torch
from thop import profile
from thop import clever_format

import os
import sys
import time

import globalvar as gl


from models import indi00000_00002
#from models import indi00031_00028

if __name__ == '__main__':
    filename = "indi00000_00002"

    model = indi00000_00002.EvoCNNModel()

    gl.set_value("pwd", sys.path[0])

    gl.set_value("cur_time", int(time.time()))
    
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