
from subprocess import Popen, run, PIPE, TimeoutExpired
import os
from itertools import cycle
from glob import glob

class tmp_chdir():
    """
    A context manager:
    temporary switch working dir to path, and return to original one
    """
    def __init__(self, path):
        self.original_path = os.getcwd()
        self.cd_path = path

    def __enter__(self):
        os.chdir(self.cd_path)
        return self.cd_path

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.original_path)

# -----action utility function-----
def _run_executable(cmd_args, exec_stdin, timeout=5):
    """ run cmd and get output """
    proc = Popen(cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    try:
        bytes_stdin = bytes(exec_stdin, "utf-8")
        outs, errs = proc.communicate(bytes_stdin, timeout=timeout)
    except TimeoutExpired:
        proc.kill()
        print("exec exceed {} seconds.".format(timeout))
        outs, errs = proc.communicate(exec_stdin, timeout=timeout)

    return outs, errs
def _run_testcase(exec_file, test_case):
    """
    testcase: list
    element is a dict have two keys "test_input", "expect_output"
    """
    testcase_logs = []
    
    for t in test_case:
        # exec_result = (outs, errs)
        exec_result = _run_executable(\
            "./{}".format(exec_file), t["test_input"]
        )

        outs, errs = map(lambda s: s.decode("utf-8"), exec_result)
        log = {
            "status": "pass" if outs.rstrip() == t["expect_output"] else "fail",
            "test_input": t["test_input"],
            "expect_output": t["expect_output"],
            "exec_stdout": outs,
            "exec_stderr": errs
        }
        testcase_logs.append(log)
    
    return testcase_logs

def _highlight(ori_str, red="fail", green="succeed"):
    return ori_str\
        .replace(red, "\033[41m\033[37m{}\033[39m\033[49m".format(red))\
        .replace(green, "\033[42m\033[37m{}\033[39m\033[49m".format(green))

def get_question_data(func):
    "decorator of error handling when get judge files data"
    def decoorator(*args, **kwarg):
        try:
            func(*args, **kwarg)
        except KeyError as err:
            print("the student didn't write this question: ", err) 
        except Exception as inst:
            print("error happened")
            print(type(inst))
            print(inst)
    
    return decoorator

# -----status utility function-----

def _collect_dir():
    """ collect midterm dir path """
    # collect all the midterm dir path
    midterm_dir_glob = glob("*term*", recursive=True)

    # create dict to map student number -> midterm dir
    midterm_dir = {}

    for i_dir in midterm_dir_glob:
        midterm_dir[i_dir[-7:]] = i_dir

    return midterm_dir

def _get_all_cfiles_in_dir(path):
    """ return all file name in path dir """
    files_path = glob("{}/*.c".format(path))

    files_name = [os.path.basename(p) for p in files_path]

    return files_name

def _compile_cfile(file_name):
    o_filename = file_name.split(".")[0]
    process_status = run(
        ["gcc", file_name, "-o", o_filename], 
        capture_output=True
    )
    compile_res = {
        "status": "succeed" if process_status.returncode == 0 else "fail",
        "returncode": process_status.returncode,
        "exec_filename": o_filename,
        "stdout": process_status.stdout.decode("utf-8"),
        "stderr": process_status.stderr.decode("utf-8")
    }
    return o_filename, compile_res

def _compile_all_in_dir(path):
    """ compile .c files in the path dir """
    # get all c files in the Midterm path
    cfiles = _get_all_cfiles_in_dir(path)
    compile_logs = {}

    with tmp_chdir(path) as _:
        # compile all the file
        for f_name in cfiles:
            o_filename, compile_res = _compile_cfile(f_name)
            compile_logs[o_filename] = compile_res

    return compile_logs

def _judge_idx(filename, idx_list):
    question_number = \
        os.path.basename(filename).split(".")[0][8:]\
            .replace("-", "").replace("_", "").replace("(", "").replace(")", "")
    for i in idx_list:
        if i in question_number:
            return i 
    
    return None

def _split_source_and_exec(files, idx_list):
    exec_f = {}
    source_f = {}
    for f in files:
        filename, ext = os.path.splitext(os.path.basename(f))
        idx = _judge_idx(filename, idx_list)
        if idx is None:
            print("invalid filename: {}".format(f))
        if ext == ".c":
            source_f[idx] = f
        else:
            exec_f[idx] = f
    return source_f, exec_f