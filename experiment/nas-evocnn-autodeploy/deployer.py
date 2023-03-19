import globalvar as gl
from mylog import Log

import subprocess
import selectors
import os
import paramiko

def get_local_path():
    '''
    :return:获取工程的绝对路径
    '''
    _path = os.path.dirname(os.path.dirname(__file__))
    return _path

def get_top_dest_dir():
    '''
    :return:获取算法在服务器根路径下的路径
    '''
    algo_name = "./lightweight/"
    tdd = os.path.join('~', algo_name)
    return tdd

def get_python_exec():
    # python_config = ExecuteConfig()
    # python_exec = python_config.read_ini_file('exe_path')
    python_exec = "python"
    return python_exec

def exec_cmd_remote(_cmd, need_response=True):
    p = subprocess.Popen(_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_str = ""
    stderr_str = ""

    if need_response:
        sel = selectors.DefaultSelector()
        sel.register(p.stdout, selectors.EVENT_READ)
        sel.register(p.stderr, selectors.EVENT_READ)
        stdout_ = None
        stderr_ = None
        for key, _ in sel.select():
            data = key.fileobj.readlines()

            if key.fileobj is p.stdout:
                stdout_ = data
            else:
                stderr_ = data

        if stdout_ is not None and len(stdout_) > 0:
            stdout_str = ''.join([_.decode('utf-8') for _ in stdout_])

        if stderr_ is not None and len(stderr_) > 0:
            stderr_str = ''.join([_.decode('utf-8') for _ in stderr_])

    return stdout_str, stderr_str

def makedirs(ssh_name, ssh_password, ip, dir_path, port = 22):
    _mk_cmd = 'sshpass -p \'%s\' ssh -p %d %s@%s mkdir -p \'%s\'' % (
        ssh_password, port, ssh_name, ip, dir_path)
    Log.debug('Execute the cmd: %s' % (_mk_cmd))
    _, stderr_ = exec_cmd_remote(_mk_cmd)
    if stderr_ is not None:
        Log.warn(stderr_)


def transfer_file_relative(ssh_name, ssh_password, ip, worker_name, source, dest, port = 22):
    """Use relative path to transfer file, both source and dest are relative path
    """

    top_dir = get_top_dest_dir()
    full_path_dest = os.path.join(top_dir, dest)
    full_path_source = os.path.join(get_local_path(), source)
    # full_path_source = full_path_source.replace(' ','\\\\ ')
    makedirs(ssh_name, ssh_password, ip, os.path.dirname(full_path_dest), port = port)
    _cmd = 'sshpass -p \'%s\' scp -P %d -r \'%s\' \'%s@%s:%s\'' % (
        ssh_password, port, full_path_source, ssh_name, worker_name, full_path_dest)
    subprocess.Popen(_cmd, stdout=subprocess.PIPE, shell=True).stdout.read().decode()


def sftp_makedirs(sftp_sess, dir_path):
    cwd_bak = sftp_sess.getcwd()
    dir_split = [dir_path]
    while os.path.dirname(dir_path) != '' and os.path.dirname(dir_path) != '/':
        dir_split = [os.path.dirname(dir_path)] + dir_split
        dir_path = dir_split[0]

    for dir_ in dir_split:
        try:
            # exists
            sftp_sess.stat(dir_)
        except:
            # absent
            sftp_sess.mkdir(dir_)

    sftp_sess.chdir(cwd_bak)


def sftp_transfer(sftp_sess, src_path, dst_path):
    sftp_makedirs(sftp_sess, os.path.dirname(dst_path))
    sftp_sess.put(src_path, dst_path)

# def transfer_training_files(ssh_name, ssh_password, worker_ip):
#     training_file_dep = [(v, v) for _, v in get_training_file_dependences().items()]
#     transport = paramiko.Transport((worker_ip, 22))
#     transport.connect(username=ssh_name, password=ssh_password)
#     sftp = paramiko.SFTPClient.from_transport(transport)
#     sftp.chdir('/')

#     training_file_dep = training_file_dep + [('runtime/README.MD', 'runtime/README.MD')]

#     top_dir = get_top_dest_dir()
#     for src, dst in training_file_dep:
#         full_path_source = os.path.join(get_local_path(), src)
#         full_path_dest = os.path.join(top_dir, dst).replace('~', '/home/' + ssh_name)

#         if full_path_dest.endswith('training.py'):
#             full_path_dest = os.path.join(os.path.dirname(os.path.dirname(full_path_dest)), 'training.py')
#         Log.debug('Start to sftp: `%s` ==> `%s`' % (full_path_source, full_path_dest))
#         sftp_transfer(sftp, full_path_source, full_path_dest)

#     transport.close()


def exec_python(ssh_name, ssh_password, ip, worker_name, py_file, args, python_exec=get_python_exec()):
    top_dir = get_top_dest_dir()
    py_file = os.path.join(top_dir, py_file).replace('~', '/home/' + ssh_name)
    Log.info('Execute the remote python file [(%s)%s]' % (ip, py_file))
    _exec_cmd = 'sshpass -p \'%s\' ssh %s@%s %s  \'%s\' %s' % (
        ssh_password, ssh_name, worker_name, python_exec, py_file,
        ' '.join([' '.join([k, v]) for k, v in args.items()]))
    Log.debug('Execute the cmd: %s' % (_exec_cmd))
    _stdout, _stderr = exec_cmd_remote(_exec_cmd, need_response=False)
    '''
    if _stderr:
        Log.debug(_stderr)
    elif _stdout:
        Log.debug(_stdout)
    else:
        Log.debug('No stderr nor stdout, seems the script has been successfully performed')
    '''

def analysis_benchmark_result(result):
    pass


class MachineConfig(object):
    def __init__(self) -> None:
        self.type = "linux"
        self.config = {}
        self.execProgram = ""

        self.workPath = "~"
        pass

class RaspMachineConfig(MachineConfig):
    def __init__(self, ip = "") -> None:
        super().__init__()

        self.config = {
            "user": "pi",
            "password": "",
            "ip": "192.168.30.82",
            "port": 8122,
        }

        if ip != "":
            self.config["ip"] = ip

        self.execProgram = "/home/pi/lightweight/nas-runner/build/benchncnn"

        self.workPath = "~/onebinary/lightweight"

class LabX86I7MachineConfig(MachineConfig):
    def __init__(self, ip = "") -> None:
        super().__init__()

        self.config = {
            "user": "n504",
            "password": "",
            "ip": "172.20.144.73",
            "port": 22,
        }

        if ip != "":
            self.config["ip"] = ip

        self.execProgram = "/home/n504/onebinary/lightweight/ncnnrunner/runner"

        self.workPath = "~/onebinary/lightweight"

class Binx1eMachineConfig(MachineConfig):
    def __init__(self, ip = "") -> None:
        super().__init__()

        self.config = {
            "user": "tuduweb",
            "password": "",
            "ip": "172.16.72.144",
            "port": 8822,
        }

        if ip != "":
            self.config["ip"] = ip

        # self.execProgram = "/home/tuduweb/onebinary/lightweight/ncnnrunner/runner"
        self.execProgram = "/home/tuduweb/development/lightweight/ML-NAS/experiment/nas-evocnn-autodeploy/runner/build/benchncnn"

        self.workPath = "~/onebinary/lightweight"

def Machine_exec_benchmark(machine: MachineConfig, filesUri : str, args = {}):
    ssh_name = machine.config['user']
    ssh_password = machine.config['password']
    ip = machine.config['ip']
    worker_name = ip

    # 被执行的文件/文件夹地址
    uri = filesUri
    runner_exec = machine.execProgram
    
    result = exec_benchmark(ssh_name, ssh_password, ip, worker_name, uri, args, runner_exec, port = machine.config["port"])

    return 0, result

def exec_benchmark(ssh_name, ssh_password, ip, worker_name, filesUri, args, runner_exec="/home/pi/lightweight/runner", machine : MachineConfig = None, port = 22):
    top_dir = get_top_dest_dir()
    # filesUri = os.path.join(top_dir, filesUri).replace('~', '/home/' + ssh_name)

    Log.info('Execute the remote runner file [(%s:%d)%s]' % (ip, port, filesUri))
    # _exec_cmd = 'sshpass -p \'%s\' ssh %s@%s %s  \'%s\' %s' % (
    #     ssh_password, ssh_name, worker_name, runner_exec, filesUri,
    #     ' '.join([' '.join([k, v]) for k, v in args.items()]))

    _exec_cmd = 'sshpass -p \'%s\' ssh -p %d %s@%s %s %s %s' % (
        ssh_password, port, ssh_name, worker_name, runner_exec, filesUri,
        ' '.join([' '.join([k, v]) for k, v in args.items()]))

    Log.debug('Execute the cmd: %s' % (_exec_cmd))
    _stdout, _stderr = exec_cmd_remote(_exec_cmd, need_response=True)

    result = ""

    if _stderr:
        Log.debug("err:" + _stderr)
        result = result + _stderr

    if _stdout:
        result = result + _stdout
        Log.debug("normal:" + _stdout)
        # 正常是要这里的结果, 然后把结果进行处理..
    if not _stderr and not _stdout:
        Log.debug('No stderr nor stdout, seems the script has been successfully performed')

    return result

def Machine_transfer_file_relative(machine: MachineConfig, source: str, dest: str) -> int:
    ssh_name = machine.config['user']
    ssh_password = machine.config['password']
    ip = machine.config['ip']
    worker_name = ip

    transfer_file_relative(ssh_name, ssh_password, ip, worker_name, source, dest, port = machine.config["port"])
    return 0



if __name__ == '__main__':
    machineConfig = {
        "type": "linux",
        "config": {
            "user": "pi",
            "password": "",
            "execProgram": "/home/pi/lightweight/nas-runner/build/benchncnn"
        },
    }




    # 实机部署
    ## 机器种类：树莓派

    # 把模型.param发送到对应机器上
    # transfer_file_relative("pi", "raspberry", "192.168.30.82", "192.168.30.82", "/home/tuduweb/development/lightweight/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1678535127", "./demo/")
    # exec_benchmark("pi", "raspberry", "192.168.30.82", "192.168.30.82", "argnone", {})
    # 执行判别, 并获取结果

    machine = RaspMachineConfig("172.16.72.144")

    #Machine_transfer_file_relative(machine, runnerConfig["sources"], runnerConfig["dest"])
    #Machine_exec_benchmark(machine, '1678535127/ncnnModels/')

    labMachine1 = LabX86I7MachineConfig()

    x1eMachine = Binx1eMachineConfig()

    runnerConfig = {
        "sources": "/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679144358", # path or file
        "dest": "/home/pi/lightweight/demo/"
    }

    print(os.path.realpath(runnerConfig["sources"]).split('/')[-1]
          )
    
    x1eRunnerConfig = {
        "sources": "/home/n504/onebinary/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1679144358", # path or file
        "dest": "/home/tuduweb/development/demo/"
    }

    Machine_transfer_file_relative(machine, runnerConfig["sources"], runnerConfig["dest"])
    Machine_exec_benchmark(machine, '/home/pi/lightweight/demo/1679144358/ncnnModels/', args={})

    #Machine_transfer_file_relative(x1eMachine, x1eRunnerConfig["sources"], x1eRunnerConfig["dest"])
    #Machine_exec_benchmark(x1eMachine, '/home/tuduweb/development/demo/1679134959/ncnnModels/', args={})