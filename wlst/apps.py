# ============================================================================
#
# Copyright (c) 2007-2011 Integral Technology Solutions Pty Ltd, 
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

##
## apps.py
##
## This script contains functions for application deployments.

from java.io import File 
import thread
import time

#=======================================================================================
# Load required modules
#=======================================================================================

try:
	commonModule
except NameError:
	execfile('ConfigNOW/common/common.py')

#=======================================================================================
# Global variables
#=======================================================================================

appsModule = '1.0.1'

log.debug('Loading module [apps.py] version [' + appsModule + ']')

#=======================================================================================
# Deploy applications
#=======================================================================================

def deployApps(componentProperties):
	"""Deploys applications"""

	applications = componentProperties.getProperty('applications')

	if applications is None:
		log.info('No applications to deploy')
	else:
		apps = applications.split(',')
		for app in apps:
			__deployApp('application.' + app, componentProperties)

#=======================================================================================
# Undeploy applications
#=======================================================================================

def undeployApps(componentProperties):
	"""Deploys applications"""

	applications = componentProperties.getProperty('applications')

	if applications is None:
		log.info('No applications to undeploy')
	else:
		apps = applications.split(',')
		for app in apps:
			__undeployApp('application.' + app, componentProperties=componentProperties)

#=======================================================================================
# Deploy an application
#=======================================================================================

def __deployApp(appPrefix, componentProperties):
    """Deploys an application"""
	
    appName = componentProperties.getProperty(appPrefix + '.name')
    appPath = componentProperties.getProperty(appPrefix + '.path')
    targets = componentProperties.getProperty(appPrefix + '.targets')
    isRemote = componentProperties.getProperty(appPrefix +'.isRemote')

    if appPath is None or len(appPath)==0:
        appPath = componentProperties.getProperty('applications.default.deploy.path')
    appFile = appPath + File.separator + componentProperties.getProperty(appPrefix + '.file')
	
    try:
        if isRemote is not None and isRemote.upper()=='TRUE':
            log.info('Deploying application Remotely: ' + appName)
            progress = deploy(appName, appFile, targets, stageMode='stage',upload='true',remote='true')
        else:
            log.info('Deploying Application : '+appName)
            progress = deploy(appName, appFile, targets)
            #log.info('Deploying application: ' + appName)
		
            progress.printStatus()
            log.debug(str(appName) + ' has been deployed. Check state ' + str(appName) + '?=' + str(progress.getState()))
            log.debug(str(appName) + ' has been deployed. Check if ' + str(appName) + ' is completed?=' + str(progress.isCompleted()))
            log.debug(str(appName) + ' has been deployed. Check if ' + str(appName) + ' is running?=' + str(progress.isRunning()))
            log.debug(str(appName) + ' has been deployed. Check if ' + str(appName) + ' is failed?=' + str(progress.isFailed()))
            log.debug(str(appName) + ' has been deployed. Check message ' + str(appName) + '?=' + str(progress.getMessage()))
    except Exception, error:
        raise ScriptError, 'Unable to deploy application [' + appName + ']: ' + str(error)

#=======================================================================================
# Undeploy an application
#=======================================================================================

def __undeployApp(appPrefix, componentProperties):
	"""Undeploys an application"""

	appName = componentProperties.getProperty(appPrefix + '.name')
	targets = componentProperties.getProperty(appPrefix + '.targets')
	undeployTimeout = componentProperties.getProperty('applications.default.undeploy.timeout')
	
	try:
		__stopApp(appName)
		
		log.info('Undeploying application: ' + appName)
		
		progress = undeploy(appName, targets, timeout=undeployTimeout)
		log.debug(str(appName) + ' has been undeployed. Check state ' + str(appName) + '?=' + str(progress.getState()))
		log.debug(str(appName) + ' has been undeployed. Check if ' + str(appName) + ' is completed?=' + str(progress.isCompleted()))
		log.debug(str(appName) + ' has been undeployed. Check if ' + str(appName) + ' is running?=' + str(progress.isRunning()))
		log.debug(str(appName) + ' has been undeployed. Check if ' + str(appName) + ' is failed?=' + str(progress.isFailed()))
		log.debug(str(appName) + ' has been undeployed. Check message ' + str(appName) + '?=' + str(progress.getMessage()))
		if progress.isFailed():
			if str(progress.getMessage()).find('Deployer:149001') == -1:
				raise ScriptError, 'Unable to undeploy application [' + appName + ']: ' + str(progress.getMessage())
	except Exception, error:
		raise ScriptError, 'Unable to undeploy application [' + appName + ']: ' + str(error)

#=======================================================================================
# Stop an application
#=======================================================================================

def __stopApp(appName):
	"""Stops an application"""

	log.info('Stopping application: ' + appName)

	try:
		progress = stopApplication(appName)
		log.debug('Is running? ' + str(progress.isRunning()))
	except Exception, error:
		raise ScriptError, 'Unable to stop application [' + appName + ']: ' + str(error)

