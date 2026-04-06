@echo on
echo "***** batch file running" >> F:\Applications\Admissions\funnel\logs\out_bokeh.log
date /T >> F:\Applications\Admissions\funnel\logs\out_bokeh.log
time /T >> F:\Applications\Admissions\funnel\logs\out_bokeh.log

whoami 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1
echo "whoami" 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1

set BOKEH_ALLOW_WS_ORIGIN=psc-data:5006

F:
echo "F:" 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1
cd F:\Applications\Admissions\funnel
echo "cd" 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1

call C:\ProgramData\Anaconda3\condabin\activate.bat py311streamlit 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1
echo "call activate" 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1
rem call conda list 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1

echo "START bokeh server " >> F:\Applications\Admissions\funnel\logs\out_bokeh.log
bokeh serve by_stage.py funnel.py by_program.py table_by_program.py 1>> F:\Applications\Admissions\funnel\logs\out_bokeh.log 2>&1

rem pause
time /T >> F:\Applications\Admissions\funnel\logs\out_bokeh.log
echo "***** batch file exiting" >> F:\Applications\Admissions\funnel\logs\out_bokeh.log
