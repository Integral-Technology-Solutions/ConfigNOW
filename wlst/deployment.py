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

##
## deployment.py
##
## This script contains functions that configure application and library deployment

#=======================================================================================
# Import common library
#=======================================================================================

try:
    commonModule
except NameError:
    execfile('wlst/common.py')
    
#=======================================================================================
# Global variables
#=======================================================================================
    
deploymentModule = '1.0.2'

log.debug('Loading module [deployment.py] version [' + deploymentModule + ']')

def __configureDeployments(online, configProperties):
    try:
	    __configureAppDeployments(online, configProperties)
	    __configureLibraryDeployments(online, configProperties)
	    __configureStartupClasses(online, configProperties)
    except Exception, error:
	    print str(error)
	    
def __configureAppDeployments(online, configProperties):
    applications=configProperties.getProperty('wls.applications')
    if not applications is None:
        applicationsList=applications.split(',')
        cd ('/AppDeployment')
        for application in applicationsList:
    	    applicationName=configProperties.getProperty('wls.application.' + application + '.name')
    	    cd (str(applicationName))
    	    applicationTargets=configProperties.getProperty('wls.application.' + application + '.targets')
    	    log.info('Setting application ' + applicationName + ' to targets ' + applicationTargets)
    	    set ('Target',applicationTargets)
    	    cd ('..')

def __configureLibraryDeployments(online, configProperties):
    libraries=configProperties.getProperty('wls.libraries')
    if not libraries is None:
        libraryList=libraries.split(',')
        cd ('/Library')
        for library in libraryList:
       		libraryName=configProperties.getProperty('wls.library.' + library + '.name')
    		cd (str(libraryName))
    		libraryTargets=configProperties.getProperty('wls.library.' + library + '.targets')
    		log.info('Setting library ' + libraryName + ' to targets ' + libraryTargets)
    		set ('Target',libraryTargets)
    		cd ('..')
    
def __configureStartupClasses(online, configProperties):
    startupclasses=configProperties.getProperty('wls.startupclasses')
    if not startupclasses is None:
        startupClassList=startupclasses.split(',')
        cd ('/StartupClass')
        for startupClass in startupClassList:
        	startupClassName=configProperties.getProperty('wls.startupclass.' + startupClass + '.name')
    		cd (str(startupClassName))
    		startupClassTargets=configProperties.getProperty('wls.startupclass.' + startupClass + '.targets')
    		log.info('Setting startup class ' + startupClass + ' to targets ' + startupClassTargets)
    		set ('Target',startupClassTargets)
    		cd ('..')

def __configureInternalAppSubdeploymentTargets(internalApp, subdeployment, targets, configProperties):
    log.info('Setting up targets for subdeployment [ ' + subdeployment + ' ]')
    targetList = targets.split(',')
    targetArray = jarray.zeros(len(targetList), ObjectName)
    position = 0
    for target in targetList:
    	targetType = configProperties.getProperty('wls.subapplication.' + internalApp + '.subdeploymentTarget.' + target + '.targetType')
	log.info('Setting target [' + str(target) + '] to subdeployment [' + str(subdeployment) + '].')
	targetArray[position] = ObjectName('com.bea:Name=' + str(target) + ',Type=' + str(targetType))
        position = position + 1
    set('Targets', targetArray)
	
def __configureInternalAppSubdeployments(internalApp, internalAppName, internalAppSubdeployments, configProperties):
    log.info('Setting up subdeployments for [ ' + internalAppName + ' ]')
    internalAppSubdeploymentsList = internalAppSubdeployments.split(',')
    for subdeployment in internalAppSubdeploymentsList:
        try:
            cd ('/AppDeployments/' + internalAppName + '/SubDeployments/' + str(subdeployment))
            log.info('Ignoring subdeployment creation: ' + str(subdeployment) + ' already exists.')
        except Exception, error:
            cd('/AppDeployments/' + str(internalAppName))
	    cmo.createSubDeployment(str(subdeployment))
	    cd ('SubDeployments/' + str(subdeployment))
        targets=configProperties.getProperty('wls.subapplication.' + internalApp + '.subdeployment.' + subdeployment + '.targets')
        if not targets is None:
            __configureInternalAppSubdeploymentTargets(internalApp, subdeployment, targets, configProperties)
    		
def configureSubApplications(configProperties):
    try:
	    internalApps=configProperties.getProperty('wls.subapplications')
	    if not internalApps is None:
		log.info('Setting up applications')
		internalAppsList=internalApps.split(',')
		for internalApp in internalAppsList:
			internalAppName=configProperties.getProperty('wls.subapplication.' + internalApp + '.name')
			internalAppSubdeployments=configProperties.getProperty('wls.subapplication.' + internalApp + '.subdeployments')
			if not internalAppSubdeployments is None:
				__configureInternalAppSubdeployments(internalApp, internalAppName, internalAppSubdeployments, configProperties)
    except Exception, error:
	    log.error(str(error))