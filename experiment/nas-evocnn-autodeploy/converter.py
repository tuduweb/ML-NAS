from torchsummary import summary

from models import indi00000_00000

if __name__ == '__main__':
    model = indi00000_00000.EvoCNNModel()
    summary(model.cuda(), (3, 32, 32), batch_size=16)