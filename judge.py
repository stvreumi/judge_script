from glob import glob
from subprocess import Popen, run, PIPE, TimeoutExpired
from itertools import cycle
import os
import pprint
import json
import shlex
import json

pp = pprint.PrettyPrinter(indent=2)

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

TEST_CASE_SUITE = {
    "1":  [
        {
            "test_input": "You are Right!!!\n",
            "expect_output": "!!!thgiR era uoY"
        },
        {
            "test_input": "This is 1 0 0 points.\n",
            "expect_output": ".stniop 0 0 1 si sihT"
        },
        {
            "test_input": "0\n",
            "expect_output": "0"
        }
    ],
    "2": [
        {
            "test_input": "4\n",
            "expect_output": "Enter a dollar amount: $20 bills: 0\n$10 bills: 0\n$5 bills: 0\n$1 bills: 4"
        },
        {
            "test_input": "90\n",
            "expect_output": "Enter a dollar amount: $20 bills: 4\n$10 bills: 1\n$5 bills: 0\n$1 bills: 0"
        },
        {
            "test_input": "2019\n",
            "expect_output": "Enter a dollar amount: $20 bills: 100\n$10 bills: 1\n$5 bills: 1\n$1 bills: 4"
        }
    ],
    "3": [
        {
            "test_input": "This alphabet is so long\n",
            "expect_output": "Enter a message: In B1FF-speak: TH15 4LPH483T 15 50 L0NG!!!!!!!!!!"
        },
        {
            "test_input": "I want enter number 10\n",
            "expect_output": "Enter a message: In B1FF-speak: 1 W4NT 3NT3R NUM83R 10!!!!!!!!!!"
        },
        {
            "test_input": "What's C++?\n",
            "expect_output": "Enter a message: In B1FF-speak: WH4T'5 C++?!!!!!!!!!!"
        }
    ],
    "4": [
        {
            "test_input": "1/1/2000\n",
            "expect_output": "Enter a date (mm/dd/yyyy): You entered the date January 1, 2000"
        },
        {
            "test_input": "4/30/2009\n",
            "expect_output": "Enter a date (mm/dd/yyyy): You entered the date April 30, 2009"
        },
        {
            "test_input": "11/11/2019\n",
            "expect_output": "Enter a date (mm/dd/yyyy): You entered the date November 11, 2019"
        }
    ]
}
TEST_CASE_SUITE_IDX = "1,2,3,4".split(",")
QUESTION_IDX = "1a,1b,2,3,4".split(",")

def collect_dir():
    """ collect midterm dir path """
    # collect all the midterm dir path
    midterm_dir_glob = glob("*term*", recursive=True)

    # create dict to map student number -> midterm dir
    midterm_dir = {}

    for i_dir in midterm_dir_glob:
        midterm_dir[i_dir[-7:]] = i_dir

    return midterm_dir

    
def print_student_list(student_list):
    # create a cycle iterater to print column number of student number in a line
    col_num_list = tuple(range(4))
    col_count = cycle(col_num_list)

    print("list all available student's submission:")
    for i_num in student_list:
        col_idx = next(col_count)
        if col_idx == col_num_list[-1]:
            print(i_num)
        else:
            print(i_num, end="  ")
        
    print("")

"""
def compile_makefile(path):
    makefile_str = "%.o: %.c\n\tgcc $< -o $@"
    with open(os.path.join(path, "Makefile"), "w") as f:
        print(makefile_str, file=f)
    cmd = "cd {}; makefile".format(path)
"""

def get_all_cfiles_in_dir(path):
    """ return all file name in path dir """
    files_path = glob("{}/*.c".format(path))

    files_name = [os.path.basename(p) for p in files_path]

    return files_name

def compile_all_in_dir(path):
    """ compile .c files in the path dir """
    # get all c files in the Midterm path
    cfiles = get_all_cfiles_in_dir(path)
    compile_logs = {}

    with tmp_chdir(path) as _:
        # compile all the file
        for f_name in cfiles:
            o_filename, compile_res = compile_cfile(f_name)
            compile_logs[o_filename] = compile_res

    return compile_logs

def compile_cfile(file_name):
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

def print_compile_status(compile_logs):
    print("Compile status:\n")
    pp.pprint(compile_logs)
            
def run_executable(cmd_args, exec_stdin, timeout=5):
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

def judge_idx(filename, idx_list):
    question_number = os.path.basename(filename).split(".")[0][8:]
    for i in idx_list:
        if i in question_number:
            return i 
    
    return None


def run_testcase(exec_file):
    """
    testcase: list
    element is a dict have two keys "test_input", "expect_output"
    """
    test_case_idx = judge_idx(exec_file, TEST_CASE_SUITE_IDX)
    if test_case_idx is None:
        log = [{ "error": "filename error" }]
        return log
    
    test_case = TEST_CASE_SUITE[test_case_idx]
    testcase_logs = []
    
    for t in test_case:
        # exec_result = (outs, errs)
        exec_result = run_executable(\
            "./{}".format(exec_file), t["test_input"]
        )

        outs, errs = map(lambda s: s.decode("utf-8"), exec_result)
        log = {
            "status": "PASS" if outs.rstrip() == t["expect_output"] else "FAIL",
            "test_case_idx": test_case_idx,
            "test_input": t["test_input"],
            "expect_output": t["expect_output"],
            "exec_stdout": outs,
            "exec_stderr": errs
        }
        testcase_logs.append(log)
    
    return testcase_logs

def split_source_and_exec(files):
    exec_f = {}
    source_f = {}
    for f in files:
        filename, ext = os.path.splitext(os.path.basename(f))
        idx = judge_idx(filename, QUESTION_IDX)
        if idx is None:
            print("invalid filename: {}".format(f))
        if ext == ".c":
            source_f[idx] = f
        else:
            exec_f[idx] = f
    return source_f, exec_f

def judge_student(student_num, student_dir):
    help_message = \
"""
l: list all available source code
v [filename key]: see the source code
j [filename key]: run the test case and see the output
r [filename key]: run the obj directly
s [question number] [score]: give score on specific question
c [question number] "comment string": give specific question comment,
    and explain why it can't get the score
exit: exit current student judge process and save the score and comment
"""
    output_json_name = "{}_result.json".format(student_num)
    print("compile first...")
    if os.path.exists(output_json_name):
        ans = input("alread have result({}), still run again?(y/n)?")
        if ans == "y":
            pass
        else:
            print("go back...")
    compile_logs = compile_all_in_dir(student_dir)
    print_compile_status(compile_logs)
    files = glob("{}/*".format(student_dir))
    
    source_f, exec_f = split_source_and_exec(files)
    score = {}
    comment = {}
    testcase_log = {}
    while True:
        try:
            cmd_string = input("{} > ".format(student_num))
            cmd_split = shlex.split(cmd_string)
            pp.pprint(cmd_split)
            if cmd_split[0] == "help":
                print(help_message)
            elif cmd_split[0] == "l":
                print("source file:")
                pp.pprint(source_f)
                print("compiled file")
                pp.pprint(exec_f)
            elif cmd_split[0] == "v":
                run(["vim", source_f[cmd_split[1]]])
            elif cmd_split[0] == "j":
                log = run_testcase(exec_f[cmd_split[1]])
                pp.pprint(log)
                testcase_log[cmd_split[1]] = log
            elif cmd_split[0] == "r":
                run(["./{}".format(exec_f[cmd_split[1]])])
            elif cmd_split[0] == "s":
                exec_f[cmd_split[1]] # test key exist
                score[cmd_split[1]] = int(cmd_split[2])
            elif cmd_split[0] == "c":
                exec_f[cmd_split[1]] # test key exist
                comment[cmd_split[1]] = cmd_split[2]
            elif cmd_split[0] == "exit":
                results = {
                    "score": score,
                    "comment": comment,
                    "compile_logs": compile_logs,
                    "testcase_log": testcase_log
                }
                print("scores: ")
                pp.pprint(results["score"])
                print("comments: ")
                pp.pprint(results["comment"])
                break
            else:
                print("unknown command:{}".format(cmd_string))
                print("try again")
        except KeyError as err:
            print("the student didn't write this question: ", err) 
        except Exception as inst:
            print("error happened")
            print(type(inst))
            print(inst)
        
    with open(output_json_name, "w") as f:
        json.dump(results, f, indent=2)



if __name__ == "__main__":
    midterm_dir = collect_dir()
    # get list of available student number
    student_list = tuple(midterm_dir.keys())

    print_student_list(student_list)

    while True:
        cmd = input("main > ")
        if cmd in student_list:
            judge_student(cmd, midterm_dir[cmd])
        elif cmd == "list":
            student_list = tuple(midterm_dir.keys())
        elif cmd == "exit":
            break
        else:
            print("unknow command or number:{}".format(cmd))
            print("try again")