import os
import argparse

from analysis import analysis_log


def generate_log():
    runtimeTargets = [
        # "/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/nsga_net_0317",
        # "/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/aecnn_0317",
        #"/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/evocnn_0317",
        "/home/n504/onebinary/ENAS_6379/runtime/MO_evocnn_MNIST_review",
    ]

    for target in runtimeTargets:
        
        # object
        targetPaths = {
            "logPath": os.path.realpath(os.path.join(target, "log")),
            "scriptPath": os.path.realpath(os.path.join(target, "scripts"))
        }

        for _path in targetPaths.values():
            if not os.path.exists(_path):
                print("{path} not exist")
                exit(-1)

        # files = analysis_log.get_file(targetPaths["logPath"],  ".txt", [])
        
        # for logFile in files:
        #     print(analysis_log.analysisOneLogFile(logFile))

        logParsedResult = analysis_log.analysis_log_for_files(targetPaths["logPath"])

        # 还想要获取参数量 等信息
        for item in logParsedResult:
            scriptUri = item["name"] + ".py"
            print(os.path.join(targetPaths["scriptPath"], scriptUri))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='bin Neural Network pytorch Arch')
    parser.add_argument('--cuda', '-c', help='是否应用cuda', default=0)
    parser.add_argument('-task', '--task', help='任务种类', default="log")
    global_args = parser.parse_args()

    if global_args.task == "log":
        generate_log()

