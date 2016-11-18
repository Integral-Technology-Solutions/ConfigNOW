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

import os
import sys
import validation_helper as helper

from java.io import File
from java.lang import System
from org.apache.log4j import Logger

log = Logger.getLogger('validation')

def sanityCheckDomainConfig(domainProperties):

    error = 0

    username = domainProperties.getProperty('wls.admin.username')
    if username is None or len(username)==0:
        error = 1
        log.error('Please verify wls.admin.username property if it exists in configuration.')
    else:
        log.debug('Admin username [' + str(username) + '] is valid.')
    
    validateAdminPassword(domainProperties)
    
    adminservername = domainProperties.getProperty('wls.admin.name')
    if adminservername is None or len(adminservername)==0:
        error = 1
        log.error('Please verify wls.admin.name property if it exists in configuration.')
    else:
        log.debug('Admin server name property [' + str(adminservername) + '] is valid.')

	prompt=domainProperties.getProperty('password.prompt')
	if prompt is not None and prompt.lower()=='true':
		__checkJdbcPasswords(domainProperties)

    if error:
        sys.exit()

def validateAdminPassword(domainProperties):
    error=0
    
    admin_password = domainProperties.getProperty('wls.admin.password')
    prompt=domainProperties.getProperty('password.prompt')
        
    if admin_password is None or len(admin_password)==0:
        if prompt is not None and prompt.lower()=='true':
            admin_username=domainProperties.getProperty('wls.admin.username')
            if admin_username and not admin_password:
            	dont_match=1
            	while dont_match:
					print 'Please enter WebLogic admin password: '
					#admin_password1=raw_input()
					admin_password1=System.console().readPassword().tostring()
					print 'Please re-enter the WebLogic admin password: ' 
					admin_password2=System.console().readPassword().tostring()
					
					if admin_password1==admin_password2:
						dont_match=0
					else:
						print 'PASSWORDS DO NOT MATCH'
                domainProperties.setProperty('wls.admin.password',admin_password1)    
        else:
            log.error('Please verify wls.admin.password property exists in configuration.')
            error=1
    else:
        log.debug('Admin password is valid.')
        
    if error:
        sys.exit()

def sanityCheckOnlineConfig(cfg):
	error=0
	nmPassword=cfg.getProperty('nodemanager.password')
	nmUsername=cfg.getProperty('nodemanager.username')
	prompt=cfg.getProperty('password.prompt')
	if nmUsername and not nmPassword:
		if prompt is not None and prompt.lower()=='true':
			dont_match=1
			while dont_match:
				print 'Please enter the Nodemanager password: '
				nm_password1=System.console().readPassword().tostring()
				print 'Please re-enter the Nodemanager password: ' 
				nm_password2=System.console().readPassword().tostring()
				if nm_password1==nm_password2:
					dont_match=0
				else:
					print 'PASSWORDS DO NOT MATCH'
			cfg.setProperty('nodemanager.password', nm_password1)
		else:
			log.error('Please verify nodemanager.password property exists in configuration')
			error = 1
	if error:
		sys.exit()

def __checkJdbcPasswords(domainProperties):
	# Check if global.jdbc.password flag is set to determine if the same JDBC password is to be used for each datasource.
	globalJdbcPasswordEnabled = domainProperties.getProperty('global.jdbc.password')
	jdbcDatasources=domainProperties.getProperty('jdbc.datasources')
	if jdbcDatasources:
		jdbcList=jdbcDatasources.split(',')
		for datasource in jdbcList:
			dsPassword=None
			dsPassword=domainProperties.getProperty('jdbc.datasource.' + str(datasource) + '.Password')
			if not dsPassword:
				if globalJdbcPasswordEnabled:
					globalJdbcPasswordValue = domainProperties.getProperty('global.jdbc.password.value')
					if not globalJdbcPasswordValue:
						log.info('Property global.jdbc.password is set, which indicates that all JDBC data sources have the same password.')
						dont_match=1
						while dont_match:
							print 'Please enter the password for all JDBC data sources: '
							password1=System.console().readPassword().tostring()
							print 'Please re-enter the password for all JDBC data sources: '
							password2=System.console().readPassword().tostring()
							if password1==password2:
								dont_match=0
							else:
								print 'PASSWORDS DO NOT MATCH'
						domainProperties.setProperty('global.jdbc.password.value', password1)
						globalJdbcPasswordValue=password1
					domainProperties.setProperty('jdbc.datasource.' + str(datasource) + '.Password', globalJdbcPasswordValue)
				else:   
					print 'Please enter password for JDBC data source [' + str(datasource) + '] :'
					password=System.console().readPassword().tostring()
					domainProperties.setProperty('jdbc.datasource.' + str(datasource) + '.Password', password)

def sanityCheckInstall(domainProperties):

    beahome = domainProperties.getProperty('wls.oracle.home')

    helper.printHeader('[VALIDATING] wls.oracle.home property')

    if beahome is None or len(beahome)==0:
        raise Exception("Required property wls.oracle.home does not exist.")
    else:
        homeDir = File(beahome)
        if not homeDir.exists():
            log.error("Property wls.oracle.home refers to an installation directory " + beahome + " that does not exist.")
            sys.exit()
        else:
            log.debug('wls.oracle.home directory [' + str(beahome) + '] exists.')

    helper.printHeader('[VALIDATING] WebLogic directory property')

    wls = domainProperties.getProperty('wls.name')
    wlsDir = File(str(beahome) + File.separator + str(wls)) 
    if not wlsDir.exists():
        log.error('WebLogic directory does not exist in wls.oracle.home directory, please verify wls.name and wls.oracle.home property.')
        sys.exit()
    else:
        log.debug('WebLogic directory [' + str(wls) + '] exists in ' + beahome)

    helper.printHeader('[VALIDATING] wls.domain.javahome property')

    javahome = domainProperties.getProperty('wls.domain.javahome')
    javahomeDir = File(str(javahome))
    if not javahomeDir.exists():
        log.error('JAVA_HOME directory ' + str(javahomeDir) + ' does not exist, please verify wls.domain.javahome property.')
        sys.exit()
    else:
        log.debug('JAVA_HOME directory [' + str(javahome) + '] exists.')
        
	validTemplates=validateTemplates(domainProperties)
	if not validTemplates:
		sys.exit()

def validateTemplates(domainProperties):  
    valid = 1
    templates = domainProperties.getProperty('wls.templates')
    if not templates is None and len(templates)>0:
        helper.printHeader('[VALIDATING] Domain Templates')
        templateList = templates.split(',')
        for template in templateList:
            templateFile = domainProperties.getProperty('wls.template.' + str(template) + '.file')
            if not templateFile is None:
                if not File(templateFile).exists():
                    valid = 0
                    log.error('Template defined in property wls.template.' + str(template) + '.file does not exist: ' + templateFile)
                    if templateFile.find('wlsb')>-1:
                        log.info('Suggested fix: Ensure OSB is installed.')
                    if templateFile.find('oracle.soa_template_11.1.1')>-1:
                        log.info('Suggested fix: Ensure SOA Suite 11g is installed.')
                else:
                    log.debug('Template ' + templateFile + ' is valid.')
    return valid