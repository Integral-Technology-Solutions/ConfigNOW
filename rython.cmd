@echo off
set redback_cp=./jython21.jar;%classpath%
java -classpath "%redback_cp%" -Dpython.home=. org.python.util.jython
