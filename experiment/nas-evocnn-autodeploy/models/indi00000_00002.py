"""
2023-02-27  16:58:03
"""
from __future__ import print_function
from torchsummary import summary
import torch.nn as nn
import torch.nn.functional as F
import math
import torch


class SamePad2d(nn.Module):
    # Mimics tensorflow's 'SAME' padding.

    def __init__(self, kernel_size, stride):
        super(SamePad2d, self).__init__()
        self.kernel_size = torch.nn.modules.utils._pair(kernel_size)
        self.stride = torch.nn.modules.utils._pair(stride)

    def forward(self, input):
        in_width = input.size()[2]
        in_height = input.size()[3]
        out_width = math.ceil(float(in_width) / float(self.stride[0]))
        out_height = math.ceil(float(in_height) / float(self.stride[1]))
        pad_along_width = ((out_width - 1) * self.stride[0] +
                           self.kernel_size[0] - in_width)
        pad_along_height = ((out_height - 1) * self.stride[1] +
                            self.kernel_size[1] - in_height)
        pad_left = math.floor(pad_along_width / 2)
        pad_top = math.floor(pad_along_height / 2)
        pad_right = pad_along_width - pad_left
        pad_bottom = pad_along_height - pad_top
        return F.pad(input, (pad_left, pad_right, pad_top, pad_bottom), 'constant', 0)

    def __repr__(self):
        return self.__class__.__name__

class EvoCNNModel(nn.Module):
    def __init__(self):
        super(EvoCNNModel, self).__init__()
        # all unit
        self.pad0 = SamePad2d(kernel_size=(9, 9), stride=(1, 1))
        self.op0 = nn.Conv2d(in_channels=3, out_channels=36, kernel_size=(9, 9), stride=(1, 1), padding=0)
        nn.init.normal_(self.op0.weight, -0.012158, 0.459613)
        self.pad1 = SamePad2d(kernel_size=(5, 5), stride=(1, 1))
        self.op1 = nn.Conv2d(in_channels=36, out_channels=15, kernel_size=(5, 5), stride=(1, 1), padding=0)
        nn.init.normal_(self.op1.weight, -0.419838, 0.252802)
        self.op4 = nn.Linear(in_features=240, out_features=10)
        nn.init.normal_(self.op4.weight, 0.444124, 0.213209)


    def forward(self, x):
        out_0 = self.pad0(x)
        out_0 = self.op0(out_0)
        out_1 = self.pad1(out_0)
        out_1 = self.op1(out_1)
        out_2 = F.avg_pool2d(out_1, 2)
        out_3 = F.max_pool2d(out_2, 4)
        out_3 = out_3.view(out_3.size(0), -1)
        out_4 = self.op4(out_3)
        return out_4


if __name__ == '__main__':
    model = EvoCNNModel()
    summary(model.cuda(), (3, 32, 32), batch_size=16)