@echo on
echo "***** batch file running" >> F:\Applications\Admissions\funnel\logs\out_stage_data.log
date /T >> F:\Applications\Admissions\funnel\logs\out_stage_data.log
time /T >> F:\Applications\Admissions\funnel\logs\out_stage_data.log

whoami 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1
echo "whoami" 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1

F:
echo "F:" 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1
cd F:\Applications\Admissions\funnel
echo "cd" 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1

call C:\ProgramData\Anaconda3\condabin\activate.bat py311streamlit 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1
echo "call activate" 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1
rem call conda list 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1

echo "START Admissions\funnel\admissions.py " >> F:\Applications\Admissions\funnel\logs\out_stage_data.log
C:\ProgramData\Anaconda3\envs\py311streamlit\python.exe admissions.py 1>> F:\Applications\Admissions\funnel\logs\out_stage_data.log 2>&1

rem pause
time /T >> F:\Applications\Admissions\funnel\logs\out_stage_data.log
echo "***** batch file exiting" >> F:\Applications\Admissions\funnel\logs\out_stage_data.log
