#!/bin/bash


function set_env {
    if [ -f setenv.sh ]; then
       echo found setenv.sh
       . setenv.sh
    fi
    relevantBits=`echo $CLASSPATH | grep weblogic.jar`
    if [ ${#relevantBits} -eq 0 ]; then
        run_jython
    else
       redback_cp="./core/engine/lib/ant-contrib-1.0b1.jar:./core/engine/lib/xmltask.jar:./core/engine/lib/log4j-1.2.17.jar:./core/engine/lib/commons-logging-1.2.jar:./core/engine/lib/jsch-0.1.51.jar:./core/engine/lib/ant.jar:./core/engine/lib/ant-launcher.jar:./core/engine/lib/ant-apache-log4j.jar:./core/engine/lib/ant-nodeps.jar:./core/engine/lib/commons-codec-1.4.jar:./core/engine/lib/commons-exec-1.1.jar:./core/engine/lib/tomcat-coyote.jar:./core/engine/lib/tomcat-util.jar:./core/engine/lib/tomcat-juli.jar:./core/engine/lib/catalina-ant.jar:.:"
       java -classpath "${redback_cp}":${CLASSPATH}  -Duser.timezone='UTC' weblogic.WLST core/engine/main.py ${args[0]} ${args[1]} ${args[2]} ${args[3]} ${args[4]} ${args[5]} ${args[6]} ${args[7]} ${args[8]}
       if [ "$?" -eq 3 ]; then
        echo call set_env again.
        set_env
       fi
    fi
}

function run_jython {
    redback_cp="./core/engine/lib/ant-contrib-1.0b1.jar:./core/engine/lib/xmltask.jar:./core/engine/lib/log4j-1.2.17.jar:./core/engine/lib/commons-logging-1.2.jar:./core/engine/lib/jsch-0.1.51.jar:./core/engine/lib/ant.jar:./core/engine/lib/ant-launcher.jar:./core/engine/lib/ant-apache-log4j.jar:./core/engine/lib/ant-nodeps.jar:./core/engine/lib/commons-codec-1.4.jar:./core/engine/lib/commons-exec-1.1.jar:./core/engine/lib/tomcat-coyote.jar:./core/engine/lib/tomcat-util.jar:./core/engine/lib/tomcat-juli.jar:./core/engine/lib/catalina-ant.jar:./jython21.jar"
    java -classpath "${redback_cp}":"${CLASSPATH}"  -Duser.timezone='UTC' -Dpython.home=. org.python.util.jython core/engine/main.py ${args[0]} ${args[1]} ${args[2]} ${args[3]} ${args[4]} ${args[5]} ${args[6]} ${args[7]} ${args[8]}

    if [ "$?" -eq 3 ]; then
        echo call set_env again.
        set_env
    fi
}
function java_exists {
	java -version &> /dev/null
        if [ "$?" -ne 0 ]; then
		echo java not found.Please ensure that you have java installed and PATH environment variable refers to correct JAVA installation directory and is exported.
                exit 1 
        fi
}	
##############
#    Main
##############
java_exists
if test -z "$1"
then
    echo 'no arguments specified. please try   ./ConfigNOW.sh help    for available commands'
else
    args=("$@")
fi


export redback_cp
set_env
echo 'done'

