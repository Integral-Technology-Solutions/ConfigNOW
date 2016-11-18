# ============================================================================
#
# Copyright (c) 2007-2010 Integral Technology Solutions Pty Ltd, 
# All Rights Reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF THIRD PARTY RIGHTS.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE BE 
# LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES, OR 
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER 
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT 
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
# FOR FURTHER INFORMATION PLEASE SEE THE INTEGRAL TECHNOLOGY SOLUTIONS 
# END USER LICENSE AGREEMENT (ELUA).
#
# ============================================================================

import sys
import os
import time

from java.lang import System
from java.io import File, FileInputStream
from java.util import Properties

from org.apache.log4j import Logger, PropertyConfigurator
from org.apache.tools.ant import Project, ProjectHelper, DefaultLogger, BuildException
from org.apache.tools.ant.listener import Log4jListener

sys.path.append('core/engine/')
sys.path.append('core/validators/')
sys.path.append('core/commands')
sys.path.append('core/commands/lib')
sys.path.append('custom/commands')

import redback
import config_loader

    
True = 1
False = 0
data_linage = Properties()

def run_validators():
    config_valid = True
    validation_logger=Logger.getLogger('validation')
    for val_dir in ['core/validators', os.path.join(site_home, 'custom/validators')]:
        sys.path.append(val_dir)
        for val_name in os.listdir(val_dir):
            val_file = os.path.join(val_dir, val_name)
            if os.path.isfile(val_file) and is_jython(val_file):
                main_logger.debug('Running validator: ' + val_file)
                result = call_extension(val_file, validation_logger)
                if result == False:
                    config_valid = False

    if not config_valid:
        main_logger.error('There were validation errors with the configuration file\n\nBUILD FAILED - Invalid Configuration\n')
        sys.exit()

def call_extension(script_file,logger):
    name=os.path.splitext(os.path.split(script_file)[1])[0]
    module=__import__(name)
    if 'run' not in dir(module):
        main_logger.error('run() function missing from extension script: ' + script_file)
        sys.exit()
    func=getattr(module,'run')
    setattr(module,'True',True)
    setattr(module,'False',False)

    if logger:
        setattr(module,'log',logger)
    if get_arg_count(func) == 0:
        return module.run()
    elif get_arg_count(func) == 1:
        return module.run(rb_config)
    return None

def run_command_plugins(plugin_point):
    if site_home:
    	sys.path.append(site_home + '/custom/plugins')
    else:
    	sys.path.append('custom/plugins')
                        
    # run any global plugin for this command
    script_name = command_name + '_' + plugin_point + '.py'
    script_file = os.path.join(site_home, 'custom/plugins', script_name)
    if os.path.isfile(script_file):
        main_logger.info('running global ' + plugin_point + ' command plugin: ' + script_file)
        call_extension(script_file, Logger.getLogger(plugin_point + '_plugin'))

    # run any configured plugins for this command
    if rb_config is not None:
        plugins_list = rb_config.getProperty('plugins.' + command_name + '.' + plugin_point)
        if plugins_list is not None:
            for plugin in plugins_list.split(','):
                script_file = os.path.join(site_home, 'custom/plugins', plugin)
                if os.path.isfile(script_file):
                    main_logger.info('Running configured ' + plugin_point + ' command plugin: ' + script_file)
                    call_extension(script_file, Logger.getLogger('plugin'))
                else:
                    build_file=find_command_build_file(os.path.join(site_home, 'custom/commands/ant'),plugin)
                    if build_file:
                        run_ant_target(build_file, plugin)
                    else:
                        main_logger.warn('Configured ' + plugin_point + ' command plugin script not found: ' + script_file)

def run_ant_target(build_file, target):
    # Initializing DefaultLogger for all ant logs to go to console
    ant_logger = DefaultLogger()
    # Initializing Log4jListener to be able to log all ANT events to log file. 
    log_file = Log4jListener()
    ant_logger.setErrorPrintStream(System.err)
    ant_logger.setOutputPrintStream(System.out)
    ant_logger.setMessageOutputLevel(Project.MSG_INFO)
    
    build_fd = File(build_file)
    project = Project()

    if rb_config is not None:
        enum = rb_config.keys()
        
        while enum.hasMoreElements():
            key = enum.nextElement()
            project.setProperty(key, rb_config.getProperty(key))    
    project.setUserProperty('ant.file', build_fd.getAbsolutePath())
    project.addBuildListener(ant_logger)
    project.addBuildListener(log_file)
    project.init()
    
    helper = ProjectHelper.getProjectHelper()
    project.addReference('ant.projectHelper', helper)
    helper.parse(project, build_fd)
    project.executeTarget(target)

def load_config(env, cfg, extra_props):
    if env and cfg:
        if not cfg.endswith(".properties"):
            cfg = cfg + ".properties"
        cfg_file = os.path.join(site_home, 'config', 'environments', env, cfg)
        main_logger.info('Loading configuration from file: ' + cfg_file)
    else:
        cfg_file = None
    return config_loader.loadProperties(cfg_file, extra_props)

def get_config(cfg_arg_count):
	
    cfg_env = None
    cfg_name = None
    cfg_arg_pos = 1
    arg_props = config_loader.createEmpty()
    while cfg_arg_pos <= cfg_arg_count:
        cfg_arg = sys.argv[1 + cfg_arg_pos]
        if cfg_arg.startswith('-D'):
            cfg_prop_split = cfg_arg[2:].split('=', 1)
            cfg_prop_key = cfg_prop_split[0]
            if len(cfg_prop_split) == 1:
            	main_logger.error("You must specify a value for the property \" "+cfg_prop_key +" \"")
            	sys.exit()
            if len(cfg_prop_split) == 2:
                cfg_prop_val = cfg_prop_split[1]
            else:
                cfg_arg_pos += 1
                cfg_prop_val = sys.argv[1 + cfg_arg_pos]
                 
            if cfg_prop_val.find("${"+cfg_prop_key+"}")>-1:
                main_logger.error("Property can't reference itself.Please verify the property definition for "+cfg_prop_key)
                sys.exit()
            arg_props.setProperty(cfg_prop_key, cfg_prop_val)
        else:
            if cfg_env is None:
                cfg_env = cfg_arg
            elif cfg_name is None:
                cfg_name = cfg_arg
            else:
                main_logger.error('Too many arguments found at: ' + cfg_arg)
                sys.exit()
        cfg_arg_pos += 1
    
    if valid_env_and_cfg(cfg_name, cfg_env):
    	if cfg_env and cfg_name:
            arg_props.setProperty("ConfigNOW.config_file_location",get_config_file_location(cfg_name, cfg_env))
            arg_props.setProperty("ConfigNOW.configuration",cfg_name)
            arg_props.setProperty("ConfigNOW.environment",cfg_env)
            arg_props.setProperty('ConfigNOW.home', os.getcwd())    
    	    return load_config(cfg_env, cfg_name, arg_props)
        	    
	arg_props.setProperty('ConfigNOW.home', os.getcwd())
    return arg_props

def get_config_file_location(cfg_name,cfg_env):
    
    cfg_path=os.path.join(site_home, 'config', 'environments', cfg_env, cfg_name)
    return cfg_path

def valid_env_and_cfg(cfg_name, cfg_env):
   cfg_path=''
   if cfg_env:
        env_path=os.path.join(site_home, 'config', 'environments', cfg_env)
        if not os.path.exists(env_path):
            print_available_environments()
            main_logger.error(cfg_env + ' is not a valid environment')
            sys.exit()
        if cfg_name is not None:
            if not cfg_name.endswith(".properties"):
                cfg_name=cfg_name + '.properties'
            cfg_path=os.path.join(site_home, 'config', 'environments', cfg_env, cfg_name)
         
        if cfg_name is None or cfg_name is '' or not os.path.exists(cfg_path):
            print_available_environments()
            print_available_properties(cfg_env)
            if cfg_name is not None:
            	    main_logger.error(cfg_name + ' is not a valid configuration file')
            else:
            	    main_logger.error("Please provide a valid configuration file name.")
            sys.exit()
   return True

def print_available_environments():
    env_path=os.path.join(site_home, 'config', 'environments')
    print '\nAvailable environments are: '
    for file in os.listdir(env_path):
        if not file == '.svn':
            print '   ' + file
    print '\n'

def print_available_properties(env):
    env_path=os.path.join(site_home, 'config', 'environments', env)
    print 'Available configuration files for ' + env + ' environment are: '
    for file in os.listdir(env_path):
        if file.endswith(".properties"):
            print '   ' + file
    print '\n'
    
def env_exists(cfg_env, cfg_name):
    env_path=os.path.join(site_home, 'config', 'environments', cfg_env)
    return os.path.exists(env_path)

def setup_main_logger():
    PropertyConfigurator.configure('log4j.properties')
    return Logger.getLogger('ConfigNOW')

def setup_command_logger():
    return Logger.getLogger('ConfigNOW.' + command_name)

def bool_str(b):
    if b:
        return 'True'
    else:
        return 'False'

def usage():
    main_logger.info('Usage: ConfigNOW <command> [<environment> <config_file>]\n')    

def find_command_file():
    cmd_files = []

    # find jython scripts
    script_name = command_name + '.py'
    script_file = os.path.join('core/commands', script_name)
    if os.path.isfile(script_file):
        cmd_files.append(script_file)
    script_file = os.path.join(site_home, 'custom/commands', script_name)
    if os.path.isfile(script_file):
        cmd_files.append(script_file)
    
    # find ant build files
    build_file = find_command_build_file('core/commands/ant',command_name)
    if build_file:
        cmd_files.append(build_file)
    build_file = find_command_build_file(os.path.join(site_home, 'custom/commands/ant'),command_name)
    if build_file:
        cmd_files.append(build_file)
    
    if len(cmd_files) == 0:
        main_logger.error('Command not found: ' + command_name)
        return None
    elif len(cmd_files) == 1:
        return cmd_files[0]
    else:
        main_logger.error('Commands must have a single implementation file, multiples found:')
        for f in cmd_files:
            main_logger.error('  ' + f)
    
def find_command_build_file(build_dir, target):
    for build_name in os.listdir(build_dir):
        if is_xml(build_name):
            build_file = os.path.join(build_dir, build_name)
            if os.path.isfile(build_file):
                try:
                    build_fd = File(build_file)
                    project = Project()
                    project.setUserProperty('ant.file', build_fd.getAbsolutePath())
                    project.init()
                    helper = ProjectHelper.getProjectHelper()
                    project.addReference('ant.projectHelper', helper)
                    project.setProperty('ConfigNOW.home', os.getcwd())
                    helper.parse(project, build_fd)
                    if project.getTargets().containsKey(target):
                        return build_file
                except:
                    log.error('Ant build file ' + str(build_file) + ' could not be processed')
                    print sys.exc_info()
                    
                    
def file_has_ext(f, ext):
    return os.path.splitext(f)[1] == ext

def is_xml(f):
    return file_has_ext(f, '.xml')

def is_jython(f):
    return file_has_ext(f, '.py')

def get_arg_count(func):
    if func and callable(func):
        return func.func_code.co_argcount
    return None

def create_setenv(home_dir):
    main_logger.info('Creating setenv file')
    str_home_dir=str(home_dir)
    wls_name=rb_config.getProperty('wls.name')
    weblogic_loc=os.path.join(str_home_dir, wls_name)
    weblogic_jar_loc=os.path.join(weblogic_loc,'server/lib/weblogic.jar')
    weblogic_cp_jar_loc=os.path.join(str_home_dir, wls_name,'modules/features/wlst.wls.classpath.jar')
    weblogic_jar=File(weblogic_jar_loc)
    weblogic_cp_jar=File(weblogic_cp_jar_loc)
    separator = os.sep
    classpathSep=os.pathsep
    osb_name=rb_config.getProperty('osb.name')
    osb_jar=""
    osb_api_jar=""
    osb_wls_jar=""

    util_jar = os.getcwd() + '/core/engine/lib/ConfigNOWUtils.jar'

    if(home_dir and osb_name):
        osb_jar=os.path.join(home_dir,osb_name,'lib/osb-server-modules-ref.jar')
        osb_api_jar=os.path.join(home_dir,osb_name,'lib/sb-kernel-api.jar')
        osb_wls_jar=os.path.join(home_dir,osb_name,'lib/sb-kernel-wls.jar')
        main_logger.debug(osb_jar)

    if separator is not None and classpathSep is not None:
        pathSep=os.sep
	if classpathSep==';':
	    main_logger.info('Assumed windows operating system')
	    envfile='setenv.cmd'
	    envcommand='set CLASSPATH=' + str(weblogic_cp_jar) + classpathSep + str(weblogic_jar) + classpathSep + util_jar
	    if (osb_jar is not None and len(osb_jar) > 0):
	        envcommand += classpathSep + str(osb_jar)
                envcommand += classpathSep + str(osb_api_jar)
                envcommand += classpathSep + str(osb_wls_jar)
            envcommand +='\nset COMMON_COMPONENTS_HOME='+ str_home_dir + '/oracle_common'
            setWLSEnv=File(weblogic_loc, '/server/bin/setWLSEnv.cmd')
        else:
            main_logger.info('Assumed linux operating system')
            envfile='setenv.sh'
            envcommand='CLASSPATH=' + str(weblogic_cp_jar) + classpathSep + str(weblogic_jar) + classpathSep + util_jar
            setWLSEnv=File(weblogic_loc, '/server/bin/setWLSEnv.sh')
            if (osb_jar is not None and len(osb_jar) > 0):
	       envcommand += classpathSep + str(osb_jar)
            if weblogic_loc is not None:
               print 'weblogic_loc = ' +str(weblogic_loc)
            else:
               print 'weblogic_loc is null'
            print 'Command = ' + envcommand
            print 'setWLSEnv = ' +str(setWLSEnv)
            envcommand=envcommand + '\n. ' + str(setWLSEnv)  + ' > /dev/null'
            envcommand=envcommand +'\nexport COMMON_COMPONENTS_HOME='+ str_home_dir + '/oracle_common'

    if weblogic_jar.exists():
        if os.path.isfile(envfile):
            os.remove(envfile)
        setenv=open(envfile,'w')
        setenv.write(envcommand)
        setenv.close()
        main_logger.info('Located weblogic.jar at ' + str(weblogic_jar))
        return True
    else:
        main_logger.debug('Could not find JAR file ' + weblogic_jar.getAbsolutePath()+'Please check wls.oracle.home and wls.name properties')
        if os.path.exists(envfile):
            os.remove(envfile)
        envcommand='set CLASSPATH=' + util_jar
        setenv=open(envfile,'w')
        setenv.write(envcommand)
        setenv.close()
        return True
		
            
def check_setenv(site_home):
    separator = os.sep
    classpathSep=os.pathsep
    if separator is not None and classpathSep is not None:
       if classpathSep==';':
           abspath = site_home+'setenv.cmd'
       else:
           abspath = site_home+'setenv.sh'
	# CONFIGNOW-101 fix
    home_dir=rb_config.getProperty('wls.oracle.home')
    wls_name=rb_config.getProperty('wls.name')
    weblogic_jar=""
    if(home_dir and wls_name):
		weblogic_cp_jar=os.path.join(home_dir,wls_name,'modules/features/wlst.wls.classpath.jar')
		weblogic_jar=os.path.join(home_dir,wls_name,'server/lib/weblogic.jar')
		main_logger.debug(weblogic_jar)
		main_logger.debug(os.path.exists(abspath))
		
		
    if os.path.exists(abspath):
    	setenv=open(abspath, 'r')
        for line in setenv.readlines():
            main_logger.debug(line)
    	    if(line.find(weblogic_jar)>-1):
    	    	main_logger.debug("setenv file is up-to-date. No need to refresh.")
    	    	setenv.close()
    	    	return True
            elif(line.find("weblogic.jar")<0):
                main_logger.debug("setenv file does not contain a reference of weblogic.jar file , probably because of wrong wls.oracle.home property.")
                setenv.close()
                return True
    	    else:
    	    	main_logger.info("setenv file is obsolete. Refreshing it.")
    	    	setenv.close()
                os.remove(abspath)
    	    	create_setenv(home_dir)
    	    	main_logger.debug('Restarting with new setenv file')
    	    	sys.exit(3)
		
    else:
		main_logger.debug("setenv file does not exist. Creating it.")
		if(os.path.exists(weblogic_jar)):
			create_setenv(home_dir)
			main_logger.debug('Restarting with new setenv file')
			sys.exit(3)
		else:
			main_logger.debug('Creation of setenv file failed. Please verify if wls.oracle.home and wls.name is correct.')
			#sys.exit()
  	    	
    	    	 	   	    	
def setup_wls_cp():
    home_dir=rb_config.getProperty('wls.oracle.home')
    wls_name=rb_config.getProperty('wls.name')
    if home_dir and wls_name:
        weblogic_loc=File(home_dir + '/' + wls_name)
        if weblogic_loc.exists():
            return create_setenv(home_dir)

def validate_plugin(plugin_point):
	plugins=rb_config.getProperty('plugins.' + command_name + '.' + plugin_point)
	pluginError=0
	if plugins:
		pluginList=plugins.split(',')
		for p in pluginList:
			script_file = os.path.join(site_home, 'custom/plugins', p)
			build_file=find_command_build_file(os.path.join(site_home, 'custom/commands/ant'),p)
			if not os.path.isfile(script_file) and not build_file:
				main_logger.error('Configured ' + plugin_point + ' command plugin [' + p + '] not found')
				pluginError=1
	return pluginError

def validate_plugins():
	main_logger.debug('Validating plugin points')
	v1=validate_plugin('pre')
	v2=validate_plugin('post')
	if v1 or v2:
		sys.exit()

def print_licence_info():	
    main_logger.info("=========================================================================")
    main_logger.info("ConfigNOW 4.3")
    main_logger.info("ConfigNOW command line version is available under open source licence and hence is available free for use up to 3 environments.")
    main_logger.info(" If you are intending to use ConfigNOW for more than 3 environments, please get in touch with us via product@integraltech.com.au.")
    main_logger.info("=========================================================================")

"""
	check_java_version

Ensures that the Java version used is in a supported band
"""
def check_java_version():
	java_version = System.getProperty('java.version')
	print java_version
	minor_version = int(java_version[2])
	if minor_version < 5 or minor_version > 8:
		main_logger.warn("UNSUPPORTED JAVA VERSION")
		main_logger.warn("Java version " + java_version + " is not supported by ConfigNOW. Commands may not function as intended")
		time.sleep(5)

"""

	Main program
	
"""

main_logger = setup_main_logger()
print_licence_info()
check_java_version()
#print (sys.version)


redback_reg = redback.load_redback_registry()
site_home = redback_reg.getProperty('site.home')
if site_home:
    main_logger.info('Using site home: ' + site_home)
    if not File(site_home).exists():
    	main_logger.error('Site home ' + site_home + ' does not exist.')
    	sys.exit()
else:
    site_home = ''

arg_count = len(sys.argv) - 1
if arg_count == 0:
    usage()
    sys.exit()

wlst_support = 'readTemplate' in dir()

main_logger.debug(wlst_support)
command_name = sys.argv[1]

if command_name == 'help()':                                            
    command_name = 'help'
try:
	from datetime import datetime, date, time
except ImportError:
    main_logger.debug("datetime module import failed, please check WLST support")

rb_config = get_config(arg_count - 1)
data_linage = config_loader.getDataLinage()


if rb_config:
    if(check_setenv(site_home)):
        main_logger.info("setenv file verified.")
    if not wlst_support:
        if setup_wls_cp():
            main_logger.info('Restarting with WLST support...')
            sys.exit(2)
    validation=rb_config.getProperty('validation')
    if validation is None:
        validation='on'
        rb_config.setProperty('validation',validation)
    if validation=='on':
        run_validators()
    else:
        main_logger.warn('Ignoring validation due to property validation=off')
    
try:
    customLog = rb_config.getProperty('confignow.commandlog')
    # @todo - consider moving off to separate function 
    if customLog is not None and len(customLog) > 0:
        if customLog == 'true':
            customLog = 'ConfigNOW_' + command_name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S.log")
        main_logger.info('Setting custom log file for command: "' + customLog + '"')
        inStream = FileInputStream('log4j.properties')
        logProperties = Properties()
        logProperties.load(inStream)
        logProperties.setProperty('log4j.appender.filelog.File', customLog)
        PropertyConfigurator.configure(logProperties)

    log = setup_command_logger()
	

    main_logger.info('WLST support: ' + bool_str(wlst_support))

    command_file = find_command_file()
    if command_file:
        validate_plugins()
        run_command_plugins('pre')
        if is_jython(command_file):
            main_logger.info('Running command from jython file: ' + command_file)
            # todo: investigate changing this to use call_extension(), done like this to work with wlst
            execfile(command_file)
            if 'run' in dir():
                run_arg_count = get_arg_count(run)
                
                if run_arg_count == 0:
                    if arg_count == 1:
                        run()
                    else:
                        usage()
                        main_logger.info('e.g.: ConfigNOW ' + command_name)                        
                        sys.exit()
                elif run_arg_count == 1:
                
                    if rb_config:                        
                        run(rb_config)
                    else:
                        print_available_environments()
                        usage()
                        main_logger.error('Command \'' + command_name + '\' requires <environment> <config_file> arguments')
                        main_logger.info('e.g.: ConfigNOW ' + command_name + ' local simple')                        
                        sys.exit()
                else:
                    main_logger.error('Incorrect number of command line arguments')
                    main_logger.info(run.__doc__)
                    sys.exit()
        else:
            main_logger.info('Running command ' + command_file + ' as ant target in build file: ' + command_file)
            if rb_config.size()<=0:                        
                print_available_environments()
                usage()
                main_logger.error('Command \'' + command_name + '\' requires <environment> <config_file> arguments')
                main_logger.info('e.g.: ConfigNOW ' + command_name + ' local simple')                        
                sys.exit()
            run_ant_target(command_file, command_name)
        run_command_plugins('post')
    else:
        sys.exit()

    main_logger.info('Command completed.\n\nBUILD SUCCESS\n')
except Exception, e:
    main_logger.error(str(e) + '\n\nBUILD FAILED\n')
except BuildException, be:
    main_logger.error(str(be)  + '\n\nBUILD FAILED\n')
