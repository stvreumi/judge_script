# judgeShell Command

## Start shell
put all student's dir in this repo, then run the following command:
```
python3 judgeShell.py
```

## Command

### list
list all available source code and corresponding filename key

### vim
vim [filename key]: use vim tosee the source code

### judge
judge [filename key]: run the test case and see the output

### run
run [filename key]: run the obj directly

### score
score [filename key] [score]: give score on specific question

### comment
comment [question number] "comment string": give specific question comment,and explain why it can't get the score

### done
exit current student judge process and save the score and comment

### avail
list all available students

### unjudge
list all unjudge student

### start
start [student number]: start judge [student]

### judge_status
print judgeStatus