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
        self.pad0 = SamePad2d(kernel_size=(20, 20), stride=(1, 1))
        self.op0 = nn.Conv2d(in_channels=3, out_channels=13, kernel_size=(20, 20), stride=(1, 1), padding=0)
        nn.init.normal_(self.op0.weight, -0.558281, 0.152075)
        self.pad4 = SamePad2d(kernel_size=(20, 20), stride=(1, 1))
        self.op4 = nn.Conv2d(in_channels=13, out_channels=9, kernel_size=(20, 20), stride=(1, 1), padding=0)
        nn.init.normal_(self.op4.weight, -0.665918, 0.588389)
        self.pad5 = SamePad2d(kernel_size=(7, 7), stride=(1, 1))
        self.op5 = nn.Conv2d(in_channels=9, out_channels=3, kernel_size=(7, 7), stride=(1, 1), padding=0)
        nn.init.normal_(self.op5.weight, -0.014483, 0.433874)
        self.op6 = nn.Linear(in_features=48, out_features=1482)
        nn.init.normal_(self.op6.weight, -0.903341, 0.327726)
        self.op7 = nn.Linear(in_features=1482, out_features=1393)
        nn.init.normal_(self.op7.weight, 0.522977, 0.630921)
        self.op8 = nn.Linear(in_features=1393, out_features=1380)
        nn.init.normal_(self.op8.weight, 0.708303, 0.186185)
        self.op9 = nn.Linear(in_features=1380, out_features=10)
        nn.init.normal_(self.op9.weight, -0.527396, 0.996034)


    def forward(self, x):
        out_0 = self.pad0(x)
        out_0 = self.op0(out_0)
        out_1 = F.max_pool2d(out_0, 2)
        out_2 = F.avg_pool2d(out_1, 2)
        out_3 = F.avg_pool2d(out_2, 2)
        out_4 = self.pad4(out_3)
        out_4 = self.op4(out_4)
        out_5 = self.pad5(out_4)
        out_5 = self.op5(out_5)
        out_5 = out_5.view(out_5.size(0), -1)
        out_6 = self.op6(out_5)
        out_7 = self.op7(out_6)
        out_8 = self.op8(out_7)
        out_9 = self.op9(out_8)
        return out_9


if __name__ == '__main__':
    model = EvoCNNModel()
    summary(model.cuda(), (3, 32, 32), batch_size=16)