# ============================================================================
#
# Copyright (c) 2007-2012 Integral Technology Solutions Pty Ltd, 
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
## osb.py
##
## This script contains functions for interacting with OSB
##

import getopt, sys, os
from java.io import FileInputStream
from java.io import File
from java.util import Date

import sys
import time

sys.add_package("com.bea.wli.config.customization")
from com.bea.wli.config.customization import Customization

# Properties used by script
PROPERTY_OSB_CFGS = "osb.configs"
PROPERTY_OSB_CFG_PREFIX = "osb.config."
PROPERTY_OSB_CFG_SUFFIX_FILE = ".file"
PROPERTY_OSB_CFG_SUFFIX_CUSTOM = ".file.custom"

# OSB Beans
OSB_SESSION_BEAN = "com.bea.wli.sb.management.configuration.SessionManagementMBean"
OSB_CONFIG_BEAN = "com.bea.wli.sb.management.configuration.ALSBConfigurationMBean"

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

log.debug('Loading module [osb.py] version [' + appsModule + ']')

#=======================================================================================
# Deploy OSB application
#=======================================================================================
def deployOsbCfg(componentProperties):
	"""Deploys OSB application, assuming that a connection to the OSB domain already exists"""

	configs = componentProperties.getProperty(PROPERTY_OSB_CFGS)

	if configs is None:
		log.info('No OSB configurations to deploy')
	else:
		cfgs = configs.split(',')
		for cfg in cfgs:
			log.debug("Deploying configuration for prefix '" + cfg + "'")
			__deployOsbCfg(PROPERTY_OSB_CFG_PREFIX + cfg, componentProperties)

#==============================================================================
# __deployOsbCfg
#
# Deploys an OSB configuration identified by name into the server, using a session
# name including the current time, to avoid potential naming conflicts. 
#
# Import also uses a customisation file in order to configure application.
#==============================================================================
def __deployOsbCfg(configPrefix, componentProperties):

	configJarFilename = componentProperties.getProperty(configPrefix + PROPERTY_OSB_CFG_SUFFIX_FILE)
	customisationFilename = componentProperties.getProperty(configPrefix + PROPERTY_OSB_CFG_SUFFIX_CUSTOM)
	log.info("Deploying OSB configuration from file '" + configJarFilename + "'")
	if not customisationFilename is None and len(customisationFilename) > 0:
		log.info("Customising using file '" + customisationFilename + "'")
		
	domainRuntime()
	infile = File(configJarFilename)
	# TODO - verify file exists
	infile = infile.getAbsoluteFile()  # enables server to find the file

	sessionMBean = findService("SessionManagement", OSB_SESSION_BEAN)
	sessionName = getNewSessionName()
	sessionMBean.createSession(sessionName)

	# obtain the ALSBConfigurationMBean instance that operates
	# on the session that has just been created. Notice that
	# the name of the mbean contains the session name.
        alsbSession = findService("ALSBConfiguration." + sessionName, OSB_CONFIG_BEAN)
        alsbSession.uploadJarFile(__readBytes(infile))
        plan = alsbSession.getImportJarInfo().getDefaultImportPlan()
        plan.setPreserveExistingEnvValues(false)
        alsbSession.importUploaded(plan)

	if not customisationFilename is None and len(customisationFilename) > 0:
		customiseImport(alsbSession, customisationFilename)

	# activate changes performed in the session
	sessionMBean.activateSession(sessionName, "Imported new application via " + configJarFilename)

#==============================================================================
# getNewSessionName
#
# Generates a new session name to use as part of an OSB session
#==============================================================================
def getNewSessionName():
	sessionName = "confignow-deploy_osb_config-" + Date().toString()
	sessionName = sessionName.replace(" ","")
	sessionName = sessionName.replace(":","")
	return sessionName

#==============================================================================
# customiseImport
#
# Applies a customisation file to runtime OSB environment - assumes that we
# are already connected
#==============================================================================
def customiseImport(configurationBean, customisationFilename):
	customisationFile = File(customisationFilename)
	inputstream = FileInputStream(customisationFile)
	configurationBean.customize(Customization.fromXML(inputstream))
