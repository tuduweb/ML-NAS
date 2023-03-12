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

    stdout_str = None
    stderr_str = None

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

def makedirs(ssh_name, ssh_password, ip, dir_path):
    _mk_cmd = 'sshpass -p \'%s\' ssh %s@%s mkdir -p \'%s\'' % (
        ssh_password, ssh_name, ip, dir_path)
    Log.debug('Execute the cmd: %s' % (_mk_cmd))
    _, stderr_ = exec_cmd_remote(_mk_cmd)
    if stderr_ is not None:
        Log.warn(stderr_)


def transfer_file_relative(ssh_name, ssh_password, ip, worker_name, source, dest):
    """Use relative path to transfer file, both source and dest are relative path
    """

    top_dir = get_top_dest_dir()
    full_path_dest = os.path.join(top_dir, dest)
    full_path_source = os.path.join(get_local_path(), source)
    # full_path_source = full_path_source.replace(' ','\\\\ ')
    makedirs(ssh_name, ssh_password, ip, os.path.dirname(full_path_dest))
    _cmd = 'sshpass -p \'%s\' scp -r \'%s\' \'%s@%s:%s\'' % (
        ssh_password, full_path_source, ssh_name, worker_name, full_path_dest)
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

def exec_benchmark(ssh_name, ssh_password, ip, worker_name, py_file, args, runner_exec="/home/pi/lightweight/runner"):
    top_dir = get_top_dest_dir()
    # py_file = os.path.join(top_dir, py_file).replace('~', '/home/' + ssh_name)

    Log.info('Execute the remote runner file [(%s)%s]' % (ip, py_file))
    # _exec_cmd = 'sshpass -p \'%s\' ssh %s@%s %s  \'%s\' %s' % (
    #     ssh_password, ssh_name, worker_name, runner_exec, py_file,
    #     ' '.join([' '.join([k, v]) for k, v in args.items()]))

    _exec_cmd = 'sshpass -p \'%s\' ssh %s@%s %s %s' % (
        ssh_password, ssh_name, worker_name, runner_exec,
        ' '.join([' '.join([k, v]) for k, v in args.items()]))

    Log.debug('Execute the cmd: %s' % (_exec_cmd))
    _stdout, _stderr = exec_cmd_remote(_exec_cmd, need_response=True)

    result = ""

    if _stderr:
        Log.debug("err: " + _stderr)
    elif _stdout:
        result = _stdout
        Log.debug(_stdout)
        # 正常是要这里的结果, 然后把结果进行处理..
    else:
        Log.debug('No stderr nor stdout, seems the script has been successfully performed')

    return result

if __name__ == '__main__':
    savedFileUri = "/home/n504/onebinary/lightweight/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1678535127/indi00000_00002"

    # 实机部署
    ## 机器种类：树莓派

    # 把模型.param发送到对应机器上
    transfer_file_relative("pi", "raspberry", "192.168.30.82", "192.168.30.82", "/home/tuduweb/development/lightweight/ML-NAS/experiment/nas-evocnn-autodeploy/outputs/1678535127", "./demo/")
    exec_benchmark("pi", "raspberry", "192.168.30.82", "192.168.30.82", "argnone", {})
    # 执行判别, 并获取结果