import os
import sys
import pandas as pd

import analysis_log



class Analysis_Works(object):
    pass


if __name__ == '__main__':
    # 面向当前框架系统..
    runtimePath = ""
    runtimeTargets = [
        "/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/nsga_net_0317",
        "/home/n504/onebinary/BenchENAS-review/BenchENAS_linux_platform/runtime/aecnn_0317"
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

        #print(logParsedResult)

        form_header = ['name', 'acc', 'accResults']
        df = pd.DataFrame(columns=form_header)

        for idx, item in enumerate(logParsedResult):
            df.loc[idx] = [item["name"], item["acc"], item["accResults"]]
            # print(item)

        df[["acc"]] = df[["acc"]].apply(pd.to_numeric)
        df.sort_values("acc", inplace=True, ascending=False)

        print(df)

        print("*"*20)

        pass
    pass