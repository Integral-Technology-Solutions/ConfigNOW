import sys
import os
import thread

import java.lang.Process
from org.apache.commons.exec import DefaultExecutor,CommandLine,PumpStreamHandler,DefaultExecuteResultHandler,LogOutputStream,ExecuteException
from  java.io import PrintStream,InputStreamReader,PipedInputStream,PipedOutputStream,File,FileInputStream,FileOutputStream,BufferedOutputStream
from java.util import Properties,HashMap
from org.apache.log4j import Logger


log = Logger.getLogger('run_external')

def run(props):
       
    separator = os.sep
    classpathSep=os.pathsep

    psh = PumpStreamHandler(System.out,System.err,System.in)
        
    commandstr=props.getProperty("command.with.arguments")
    if commandstr is None or commandstr=="":
    	    log.error("Please verify the command specified in edxternal_app.properties file.")
    
    dir_name=props.getProperty("working.dir")
    if dir_name is None:
    	    dir_name=os.getcwd()
    working_dir=File(dir_name)
    if working_dir is None:
    	    log.error("Please specify a valid and existing working dir in external_app.properties file")
    
    if separator is not None and classpathSep is not None:
       if classpathSep==';':
           cl = CommandLine.parse("cmd.exe")
           cl.addArgument("/C")
       else:
           cl = CommandLine.parse("sh")
  
    cl.addArguments(commandstr)
    executor=DefaultExecutor()
    executor.setWorkingDirectory(working_dir)
    executor.setStreamHandler(psh)
    log.info("\n<<<<<< LOGS FROM EXTERNAL PROCESS >>>>>>>\n")
    need_exit_value=props.getProperty("need.exit.code")
    
    if need_exit_value is 'true':
    
    	    try:
    	    	resultHandler = DefaultExecuteResultHandler()    
    	        executor.execute(cl,resultHandler)
    	        exitValue = resultHandler.waitFor()
    	    except ExecuteException, error:
    	    	log.error('Command execution failed with return code  ' + str(exitValue))    	    	
    	    
    else:
    	    try:
    	    	executor.execute(cl)
    	    except ExecuteException, error:
    	    	log.error('Command Execution Failed')
    	    	
    
def loadPropertiesFromFile(filename,props):
    newprops=Properties()
    inputstr = FileInputStream(filename)
    newprops.load(inputstr)
    inputstr.close()
    enum = newprops.keys()
    while enum.hasMoreElements():
        key = enum.nextElement()
        if props.getProperty(key) is None:
            props.setProperty(key, newprops.getProperty(key))
    return props
  
	
    

        
    
