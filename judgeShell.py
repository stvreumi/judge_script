import cmd
import shlex
from judgeAction import JudgeAction

# add docstring to the decorated function
from functools import wraps

def _check_judge_status(func):
    @wraps(func)
    def decorator(self, *args, **kwarg):
        if self.action.get_student_num() is None:
            print("this command currently not available.")
            print("start judge first")
            return
        else:
            func(self, *args, **kwarg)
    return decorator

class JudgeShell(cmd.Cmd):
    file = None
    def __init__(self, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey, stdin, stdout)
        
        self.intro = \
            "Judge Shell. Type help or ? to list commands.\n"
        self.prompt = "main > "
        self.action = JudgeAction()

    # ----- judge commands -----
    @_check_judge_status
    def do_list(self, arg):
        """list all available source code and corresponding filename key"""
        self.action.list_files()
    
    @_check_judge_status
    def do_vim(self, arg):
        """vim [filename key]: use vim tosee the source code"""
        self.action.open_with_vim(arg)
    
    @_check_judge_status
    def do_judge(self, arg):
        """judge [filename key]: run the test case and see the output"""
        self.action.run_testcase(arg)
    
    @_check_judge_status
    def do_run(self, arg):
        """run [filename key]: run the obj directly"""
        self.action.run_directly(arg)

    @_check_judge_status
    def do_score(self, arg):
        """score [filename key] [score]: give score on specific question"""
        self.action.give_score(*shlex.split(arg))

    @_check_judge_status
    def do_comment(self, arg):
        """
        comment [question number] "comment string": give specific question comment,
        and explain why it can't get the score
        """
        self.action.give_comment(*shlex.split(arg))
    
    @_check_judge_status
    def do_done(self, arg):
        """exit current student judge process and save the score and comment"""
        self.action.exit_judge()
        self.prompt = "main > "

    # ----- main commands -----
    def do_avail(self, arg):
        """list all available students"""
        self.action.list_available()

    def do_unjudge(self, arg):
        """list all unjudge student"""
        self.action.list_unjudge()


    def do_start(self, arg):
        """start [student number]: start judge [student]"""
        self.action.start(arg)
        self.prompt = "{} > ".format(self.action.get_student_num())
    
    def do_judge_status(self, arg):
        """print judgeStatus"""
        self.action.print_status()

    def complete_start(self, text, line, begidx, endidx):
        unjudge_list = self.action.get_unjudge()
        if not text:
            completions = unjudge_list
        else:
            completions = [ f for f in unjudge_list
                            if f.startswith(text)
                          ][0]
        return completions
    
    def do_exit(self, arg):
        """exit shell"""
        if self.action.get_student_num() is not None:
            self.do_done(None)
        return True
    
    # --- other ---
    def emptyline(self):
        pass

if __name__ == '__main__':
    JudgeShell().cmdloop()