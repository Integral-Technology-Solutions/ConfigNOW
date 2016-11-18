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

import validation_helper as helper
from java.io import File

def run(config):
    if validateDomainProperty(config):
            return False
    return True

def validateDomainProperty(domainProperties):
    error = 0
    
    domainMode = domainProperties.getProperty('wls.domain.mode')
    if not domainMode is None and len(domainMode)==0:
        if not domainMode == 'prod' and not domainMode == 'dev':
            error = 1
            log.error('The wls.domain.mode property supports only [prod,dev].')
        else:
            log.debug('Domain runtime mode [' + str(domainMode) + '] is valid.')
    
    domainAdminPort = domainProperties.getProperty('wls.domain.adminPort')
    if not domainAdminPort is None and len(domainAdminPort)>0:
        try:
            int(domainAdminPort)
        except ValueError:
            log.error('Please verify wls.domain.adminPort property.')
        else:
            if int(domainAdminPort)<0 or int(domainAdminPort)>65535:
                log.error('Please verify wls.domain.adminPort property, port number is not in valid range [0-65535].')
            else:
                log.debug('Domain-wide administration port [' + str(domainAdminPort) + '] is valid.')
    
    keystore = domainProperties.getProperty('wls.domain.trustKeyStore')
    if not keystore is None and len(keystore)>0:
        if not keystore == 'DemoTrust' and not keystore == 'CustomTrust':
            error = 1
            log.error('wls.domain.trustKeyStore property supports only [DemoTrust,CustomTrust].')
        else:
            log.debug('Keystore type [' + str(keystore) + '] is valid.')
    else:
        if keystore == 'CustomTrust':
            tmpkeystoreFile = domainProperties.getProperty('wls.domain.trustKeyStoreFile')
            keystoreFile = File(tmpkeystoreFile)
            if not keystoreFile.exists():
                error = 1
                log.error('File ' + str(tmpkeystoreFile) + ' does not exist, please verify wls.domain.trustKeyStoreFile property.')
            else:
                log.debug('Keystore file [' + str(tmpkeystoreFile) + '] exists.')
            
    timeout = domainProperties.getProperty('wls.domain.jta.timeout')
    if not timeout is None and len(timeout)>0:
        try:
            int(timeout)
        except:
            error = 1
            log.error('Please verify wls.domain.jta.timeout property.')
        else:
            if int(timeout)<1 or int(timeout)>2147483647:
                log.error('Please verify wls.domain.jta.timeout property, It is not in valid range [0-2147483647].')
            else:
                log.debug('Domain JTA timeout property [' + str(timeout) + '] is valid.')

    securityInteropMode = domainProperties.getProperty('wls.domain.jta.securityInteropMode')
    if not securityInteropMode is None and len(securityInteropMode)>0:
        if not securityInteropMode=='default' and not securityInteropMode=='performance' and not securityInteropMode=='compatibility':
            error = 1
            log.error('The wls.domain.jta.securityInteropMode property supports only [default,performance,compatibility, or leave blank to use default].')
        else:
            log.debug('Domain JTA Security Interop Mode property [' + str(securityInteropMode) + '] is valid.')

    authenticators = domainProperties.getProperty('wls.domain.security.authenticators')
    if not authenticators is None and len(authenticators)>0:
        authenticatorList = authenticators.split(',')
        for authenticator in authenticatorList:
            helper.printHeader('[VALIDATING] authenticator ' + str(authenticator) + ' properties')
            
            authenticatorName = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.name')
            if authenticatorName is None or len(authenticatorName)==0:
                error = 1
                log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.name property if it exists in configuration.')
            else:
                log.debug('Authenticator [' + str(authenticator) + '] name property [' + str(authenticatorName) + '] is valid.')

            authenticatorType = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.type')
            if authenticatorType is None or len(authenticatorType)==0:
                error = 1
                log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.type property if it exists in configuration.')
            else:
                if not authenticatorType=='OpenLDAP' and not authenticatorType=='ActiveDirectory':
                    error = 1
                    log.error('The wls.domain.security.authenticator.' + str(authenticator) + '.type property supports only [OpenLDAP,ActiveDirectory].')
                else:
                    log.debug('Authenticator [' + str(authenticator) + '] type property [' + str(authenticatorType) + '] is valid.')

            authenticatorPrincipal = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.principal')
            if authenticatorPrincipal is None or len(authenticatorPrincipal)==0:
                error = 1
                log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.principal property if it exists in configuration.')
            else:
                log.debug('Authenticator [' + str(authenticator) + '] principal property [' + str(authenticatorPrincipal) + '] is valid.')

            authenticatorCredential = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.credential')
            if authenticatorCredential is None or len(authenticatorCredential)==0:
                error = 1
                log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.credential property if it exists in configuration.')
            else:
                log.debug('Authenticator [' + str(authenticator) + '] credential property [' + str(authenticatorCredential) + '] is valid.')

            authenticatorHost = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.host')
            if authenticatorHost is None or len(authenticatorHost)==0:
                error = 1
                log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.host property if it exists in configuration.')
            else:
                log.debug('Authenticator [' + str(authenticator) + '] host property [' + str(authenticatorHost) + '] is valid.')

            authenticatorPort = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.port')
            if not authenticatorPort is None and len(authenticatorPort)>0:
                try:
                    int(authenticatorPort)
                except:
                    error = 1
                    log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.port property.')
                else:
                    if int(authenticatorPort)<0 or int(authenticatorPort)>65535:
                        log.error('Please verify wls.domain.security.authenticator.' + str(authenticator) + '.port property, port number is not in valid range [0-65535].')
                    else:
                        log.debug('Authenticator [' + str(authenticator) + '] port property [' + str(authenticatorPort) + '] is valid.')
            
            authenticatorSSL = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.sslEnabled')
            if not authenticatorSSL is None and len(authenticatorSSL)>0:
                if not authenticatorSSL.upper()=='TRUE' and not authenticatorSSL.upper()=='FALSE':
                    error = 1
                    log.error('The wls.domain.security.authenticator.' + str(authenticator) + '.sslEnabled property supports only [true,false].')
                else:
                    log.debug('Authenticator [' + str(authenticator) + '] ssl-enabled property [' + str(authenticatorSSL) + '] is valid.')

            authenticatorKeepAlive = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.keepAliveEnabled')
            if not authenticatorKeepAlive is None and len(authenticatorKeepAlive)>0:
                if not authenticatorKeepAlive.upper()=='TRUE' and not authenticatorKeepAlive.upper()=='FALSE':
                    error = 1
                    log.error('The wls.domain.security.authenticator.' + str(authenticator) + '.keepAliveEnabled property supports only [true,false].')
                else:
                    log.debug('Authenticator [' + str(authenticator) + '] keep-alive-enabled property [' + str(authenticatorKeepAlive) + '] is valid.')

            authenticatorGroupLookupCaching = domainProperties.getProperty('wls.domain.security.authenticator.' + str(authenticator) + '.enableSIDtoGroupLookupCaching')
            if not authenticatorGroupLookupCaching is None and len(authenticatorGroupLookupCaching)>0:
                if not authenticatorGroupLookupCaching.upper()=='TRUE' and not authenticatorGroupLookupCaching.upper()=='FALSE':
                    error = 1
                    log.error('The wls.domain.security.authenticator.' + str(authenticator) + '.enableSIDtoGroupLookupCaching property supports only [true,false].')
                else:
                    log.debug('Authenticator [' + str(authenticator) + '] enable-SID-to-group-lookup-caching property [' + str(authenticatorGroupLookupCaching) + '] is valid.')

    groups = domainProperties.getProperty('wls.domain.security.groups')
    if not groups is None and len(groups)>0:
        groupList = groups.split(',')
        for group in groupList:
            helper.printHeader('[VALIDATING] group ' + str(group) + ' properties')

            groupname = domainProperties.getProperty('wls.domain.security.group.' + str(group) + '.groupname')
            if groupname is None or len(groupname)==0:
                error = 1
                log.error('Please verify wls.domain.security.group.' + str(group) + '.groupname property if it exists in configuration.')
            else:
                log.debug('Group [' + str(group) + '] name property [' + str(groupname) + '] is valid.')

            groupauthenticator = domainProperties.getProperty('wls.domain.security.group.' + str(group) + '.authenticator')
            if groupauthenticator is None or len(groupauthenticator)==0:
                log.debug('Group [' + str(group) + '] authenticator property [' + str(authenticator) + '] is not specified, it will be defaulted to DefaultAuthenticator.')
            else:
                if groupauthenticator!='DefaultAuthenticator':
                    if not authenticators is None and len(authenticators)>0:
                        authenticatorList = authenticators.split(',')
                        exist = 0
                        for authenticator in authenticatorList:
                            if groupauthenticator==authenticator:
                                exist = 1
                                break
                        if not exist:
                            error = 1
                            log.error('Please verify wls.domain.security.group.' + str(group) + '.authenticator property and wls.domain.security.authenticators if they are configured properly.')
                        else:
                            log.debug('Group ' + str(group) + ' authenticator property [' + str(groupauthenticator) + '] is valid.')
                else:
                    log.debug('Group [' + str(group) + '] authenticator property [' + str(groupauthenticator) + '] is valid.')

    users = domainProperties.getProperty('wls.domain.security.users')
    if not users is None and len(users)>0:
        userList = users.split(',')
        for user in userList:
            helper.printHeader('[VALIDATING] user ' + str(user) + ' properties')

            username = domainProperties.getProperty('wls.domain.security.user.' + str(user) + '.username')
            if username is None or len(username)==0:
                error = 1
                log.error('Please verify wls.domain.security.user.' + str(user) + '.username property if it exists in configuration.')
            else:
                log.debug('User [' + str(user) + '] name property [' + str(username) + '] is valid.')

            userauthenticator = domainProperties.getProperty('wls.domain.security.user.' + str(user) + '.authenticator')
            if userauthenticator is None or len(userauthenticator)==0:
                log.debug('User [' + str(user) + '] authenticator property [' + str(user) + '] is not specified, it will be defaulted to DefaultAuthenticator.')
            else:
                if userauthenticator!='DefaultAuthenticator':
                    if not authenticators is None and len(authenticators)>0:
                        authenticatorList = authenticators.split(',')
                        exist = 0
                        for authenticator in authenticatorList:
                            if userauthenticator==authenticator:
                                exist = 1
                                break
                        if not exist:
                            error = 1
                            log.error('Please verify wls.domain.security.user.' + str(user) + '.authenticator property and wls.domain.security.authenticators if they are configured properly.')
                        else:
                            log.debug('User ' + str(user) + ' authenticator property [' + str(userauthenticator) + '] is valid.')
                    
                else:
                    log.debug('User [' + str(user) + '] authenticator property [' + str(userauthenticator) + '] is valid.')

    customvars = domainProperties.getProperty('wls.domain.customenvvars')
    if not customvars is None and len(customvars)>0:
        customvarList = customvars.split(',')
        for customvar in customvarList:
            helper.printHeader('[VALIDATING] Custome environment variable ' + str(customvar) + ' properties')
            
            customvarText = domainProperties.getProperty('wls.domain.customenvvar.' + str(customvar) + '.text')
            if customvarText is None or len(customvarText)==0:
                error = 1
                log.error('Please verify wls.domain.customenvvar.' + str(customvar) + '.text property if it exists in configuration.')
            else:
                if customvarText.find('=')!=-1:
                    log.debug('Custome environment variable [' + str(customvar) + '] text property [' + str(customvarText) + '] is valid.')
                else:
                    error = 1
                    log.error('Please verify wls.domain.customenvvar.' + str(customvar) + '.text property, this is applicable only for key-value pairs format [<name>=<value>].')

    domaincustomlog = domainProperties.getProperty('wls.domain.log.custom')
    if not domaincustomlog is None and len(domaincustomlog)>0:
        helper.printHeader('[VALIDATING] domain custom log properties')
        
        if not domaincustomlog.upper()=='TRUE' and not domaincustomlog.upper()=='FALSE':
            error = 1
            log.error('The wls.domain.log.custom property supports only [true,false].')
        else:
            log.debug('Domain custom log enable property [' + str(domaincustomlog) + '] is valid.')
            
            if domaincustomlog.upper()=='TRUE':                
                filename = domainProperties.getProperty('wls.domain.log.filename')
                if not filename is None and len(filename)>0:
                    file = File(filename)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please verify the user running this script has permission to create directory and file [' + str(filename) + '].')

                limitNumberOfFile = domainProperties.getProperty('wls.domain.log.limitNumOfFile')
                if not limitNumberOfFile is None and len(limitNumberOfFile)>0:
                    if not limitNumberOfFile.upper()=='TRUE' and not limitNumberOfFile.upper()=='FALSE':
                        error = 1
                        log.error('The wls.domain.log.limitNumOfFile property supports only [true,false].')
                    else:
                        log.debug('Domain log limit number of file property [' + str(limitNumberOfFile) + '] is valid.')

                fileToRetain = domainProperties.getProperty('wls.domain.log.fileToRetain')
                if not fileToRetain is None and len(fileToRetain)>0:
                    if not fileToRetain is None and len(fileToRetain)>0:
                        try:
                            int(fileToRetain)
                        except ValueError:
                            log.error('Please verify wls.domain.log.fileToRetain [' + str(fileToRetain) + '] property.')
                        else:
                            if int(fileToRetain)<1 or int(fileToRetain)>99999:
                                log.error('Please verify wls.domain.log.fileToRetain property, number is not in valid range [1-99999].')
                            else:
                                log.debug('Domain log file to retain [' + str(fileToRetain) + '] is valid.')

                logRotateOnStartup = domainProperties.getProperty('wls.domain.log.rotateLogOnStartup')
                if not logRotateOnStartup is None and len(logRotateOnStartup)>0:
                    if not logRotateOnStartup.upper()=='TRUE' and not logRotateOnStartup.upper()=='FALSE':
                        error = 1
                        log.error('The wls.domain.log.rotateLogOnStartup property supports only [true,false].')
                    else:
                        log.debug('Domain log rotate on startup property [' + str(logRotateOnStartup) + '] is valid.')

                rotationType = domainProperties.getProperty('wls.domain.log.rotationType')
                if not rotationType is None and len(rotationType)>0:
                    if not rotationType == 'bySize' and not rotationType == 'byTime':
                        error = 1
                        log.error('The wls.domain.log.rotationType property supports only [bySize,byTime].')
                    else:
                        log.debug('Domain log rotation type property [' + str(rotationType) + '] is valid.')

                    if rotationType == 'bySize':
                        fileMinSize = domainProperties.getProperty('wls.domain.log.fileMinSize')
                        if not fileMinSize is None and len(fileMinSize)>0:
                            try:
                                int(fileMinSize)
                            except ValueError:
                                log.error('Please verify wls.domain.log.fileMinSize [' + str(fileMinSize) + '] property.')
                            else:
                                if int(fileMinSize)<0 or int(fileMinSize)>65535:
                                    log.error('Please verify wls.domain.log.fileMinSize [' + str(fileMinSize) + '] property, number is not in valid range [0-65535].')
                                else:
                                    log.debug('Domain log file min size [' + str(fileMinSize) + '] is valid.')
                        
                    if rotationType == 'byTime':
                        rotationTime = domainProperties.getProperty('wls.domain.log.rotationTime')
                        if not rotationTime is None and len(rotationTime)>0:
                            if rotationTime.find(':')==-1:
                                error = 1
                                log.error('Please verify wls.domain.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                            else:
                                if len(rotationTime)<4 or len(rotationTime)>5:
                                    error = 1
                                    log.error('The wls.domain.log.rotationTime [' + str(rotationTime) + '] property, the property supports time format [HH:MM].')
                                else:
                                    log.debug('Domain log rotation time [' + str(rotationTime) + '] is valid.')
                        
                        fileTimespan = domainProperties.getProperty('wls.domain.log.fileTimeSpan')
                        if not fileTimespan is None and len(fileTimespan)>0:
                            try:
                                int(fileTimespan)
                            except ValueError:
                                log.error('Please verify wls.domain.log.fileTimeSpan [' + str(fileTimespan) + '] property.')
                            else:
                                if int(fileTimespan)<1:
                                    log.error('Please verify wls.domain.log.fileTimeSpan [' + str(fileTimespan) + '] property, number is not in valid range [>=1].')
                                else:
                                    log.debug('Domain log file timespan [' + str(fileTimespan) + '] is valid.')
 
                rotationDir = domainProperties.getProperty('wls.domain.log.rotationDir')
                if not rotationDir is None and len(rotationDir)>0:
                    file = File(rotationDir)
                    if file.isAbsolute():
                        if not file.exists():
                            log.debug('[NOTE] Please make sure if the user running this script has permission to create directory and file [' + str(rotationDir) + '].')

                fileSeverity = domainProperties.getProperty('wls.domain.log.logFileSeverity')
                if not fileSeverity is None and len(fileSeverity)>0:
                    if not fileSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Warning':
                        error = 1
                        log.error('The wls.domain.log.logFileSeverity property supports only [Debug,Info,Warning].')
                    else:
                        log.debug('Domain log file severity property [' + str(fileSeverity) + '] is valid.')
                        
                broadcastSeverity = domainProperties.getProperty('wls.domain.log.broadcastSeverity')
                if not broadcastSeverity is None and len(broadcastSeverity)>0:
                    if not broadcastSeverity == 'Trace' and not broadcastSeverity == 'Debug' and not broadcastSeverity == 'Info' and not broadcastSeverity == 'Notice' and not broadcastSeverity == 'Warning' and not broadcastSeverity == 'Error' and not broadcastSeverity == 'Critical' and not broadcastSeverity == 'Alert' and not broadcastSeverity == 'Emergency' and not broadcastSeverity == 'Off':
                        error = 1
                        log.error('The wls.domain.log.broadcastSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                    else:
                        log.debug('Domain broadcast severity property [' + str(broadcastSeverity) + '] is valid.')
                        
                memoryBufferSeverity = domainProperties.getProperty('wls.domain.log.memoryBufferSeverity')
                if not memoryBufferSeverity is None and len(memoryBufferSeverity)>0:
                    if not memoryBufferSeverity == 'Trace' and not memoryBufferSeverity == 'Debug' and not fileSeverity == 'Info' and not fileSeverity == 'Notice' and not fileSeverity == 'Warning' and not fileSeverity == 'Error' and not fileSeverity == 'Critical' and not fileSeverity == 'Alert' and not fileSeverity == 'Emergency' and not fileSeverity == 'Off':
                        error = 1
                        log.error('The wls.domain.log.memoryBufferSeverity property supports only [Trace,Debug,Info,Notice,Warning,Error,Critical,Alert,Emergency,Off].')
                    else:
                        log.debug('Domain memory buffer severity property [' + str(memoryBufferSeverity) + '] is valid.')

    return error