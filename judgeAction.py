import json
from glob import glob
import pprint
from subprocess import run
import os.path

import judge_utility

pp = pprint.PrettyPrinter(indent=2, width=60, compact=True)

QUESTION_IDX = "1a,1b,2,3,4".split(",")
with open("test_case_suite.json", "r") as f:
    TEST_CASE_SUITE = json.load(f)

class JudgeStatus():
    def __init__(self):
        # -----available students data-----
        self.midterm_dir = judge_utility._collect_dir()
        self.student_list = tuple(self.midterm_dir.keys())
        self.unjudge_list = list(self.student_list)
        self.question_idx = QUESTION_IDX

        # -----judge data-----
        self.empty_data()
    
    def __repr__(self):
        return (
            "<class JudgeStaus>\navailable number: {}\nunjudge number: {}\ncurrent judge: {}\n"\
                .format(len(self.student_list), len(self.unjudge_list), self.student_num)
        )
    def start_judge(self, student_num):
        self.student_num = student_num
        self.result_json_name = \
            JudgeStatus.get_result_json_name(self.student_num)
            
        try:
            student_dir = self.midterm_dir[self.student_num]
        except KeyError as err:
            print("No this student: {}".format(err))

        # ---compile---
        print("compile first...")
        compile_logs = judge_utility._compile_all_in_dir(student_dir)
        # print compile status
        print("Compile status:\n")
        print(judge_utility._highlight(pp.pformat(compile_logs)))

        # ---get source files and executable files---
        files = glob("{}/*".format(student_dir))
        self.source_files, self.exec_files = \
            judge_utility._split_source_and_exec(files, self.question_idx)

        # ---init logs and store compile logs---
        self.logs = {}
        self.logs["compile_logs"] = compile_logs
        self.logs["score"] = {}
        self.logs["comment"] = {}
        self.logs["testcase_log"] = {}
    
    def exit_judge(self):
        self._save_and_show_judge()
        if self.student_num in self.unjudge_list:
            self.unjudge_list.remove(self.student_num)
        self.empty_data()

    def empty_data(self):
        self.student_num = None
        self.result_json_name = None
        self.source_files = None
        self.exec_files = None
        self.logs = None

    def _save_and_show_judge(self):
        with open(self.result_json_name, "w") as f:
            json.dump(self.logs, f, indent=2)
        print("scores: ")
        pp.pprint(self.logs["score"])
        print("comments: ")
        pp.pprint(self.logs["comment"])
    
    @staticmethod
    def get_result_json_name(student_num):
        return "{}_result.json".format(student_num)

class JudgeAction():
    def __init__(self):
        self.status = JudgeStatus()
    
    def start(self, student_num):
        result_json_name = \
            JudgeStatus.get_result_json_name(student_num)
        
        # check result existness to prevent overwrite
        if os.path.exists(result_json_name):
            ans = input("alread have result({}), still run again?(y/n)?")
            if ans == "y":
                pass
            else:
                print("go back...")
                return
        
        # initialize status
        self.status.start_judge(student_num)
            
    def list_files(self):
        print("source file:")
        pp.pprint(self.status.source_files)
        print("compiled file")
        pp.pprint(self.status.exec_files)
    
    def list_available(self):
        pp.pprint(self.status.student_list)
        print("total: {}".format(len(self.status.student_list)))

    def list_unjudge(self):
        pp.pprint(self.status.unjudge_list)
        print("total: {}".format(len(self.status.unjudge_list)))
    
    def print_status(self):
        print(self.status)
        if self.get_student_num() is not None:
            print("scores: ")
            pp.pprint(self.status.logs["score"])
            print("comments: ")
            pp.pprint(self.status.logs["comment"])
    
    @judge_utility.get_question_data
    def open_with_vim(self, q_num):
        run(["vim", self.status.source_files[q_num]])
    
    @judge_utility.get_question_data
    def run_testcase(self, q_num):
        exec_file = self.status.exec_files[q_num]
        test_case = TEST_CASE_SUITE[q_num]
        log = judge_utility._run_testcase(exec_file, test_case)
        print(judge_utility._highlight(pp.pformat(log), green="pass"))
        self.status.logs["testcase_log"][q_num] = log
    
    @judge_utility.get_question_data
    def run_directly(self, q_num):
        run(["./{}".format(self.status.exec_files[q_num])])

    @judge_utility.get_question_data
    def give_score(self, q_num, score):
        self.status.exec_files[q_num]
        self.status.logs["score"][q_num] = float(score)
        pp.pprint(self.status.logs["score"])

    @judge_utility.get_question_data
    def give_comment(self, q_num, comment):
        self.status.exec_files[q_num]
        self.status.logs["comment"][q_num] = comment
    
    def exit_judge(self):
        self.status.exit_judge()
    
    def get_student_num(self):
        return self.status.student_num
    
    def get_unjudge(self):
        return self.status.unjudge_list
