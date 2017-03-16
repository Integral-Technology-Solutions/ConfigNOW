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

import common.assertions as assertions

execfile('wlst/common.py')

def run(config):
    """This is the command used to configure enterprise manager"""
    log.debug('-- in configure_em.py')

    # Assert the input configurations
    assertions.sanityCheckInstall(config)
    assertions.sanityCheckDomainConfig(config)
    assertions.sanityCheckOnlineConfig(config)

    # Configure the enterprise manager
    configure_em(config)

def configure_em(config):
    __connectAdminServer(config)
    try:
       log.info('Configure Enterprise Manager started')
       configure_system_policies(config,config)
       configure_wsm_domain(config,config)
       configure_credentials(config,config)
    except Exception, error:
       print 'Unable to update enterprise manager : ' + str(error)
       disconnect('true')
    else:
       log.info('Configure Enterprise Manager completed')

def configure_wsm_domain(resourcesProperties, domainProperties):
    log.info('Configure web service manager domain configuration')
    try:
       wsmDomain=resourcesProperties.getProperty('em.wsmKeyStore.wsmDomain')
       keyStoreType=resourcesProperties.getProperty('em.wsmKeyStore.keyStoreType')
       keyStorePassword=resourcesProperties.getProperty('em.wsmKeyStore.keyStorePassword')
       keyStorePath=resourcesProperties.getProperty('em.wsmKeyStore.keyStorePath')
       signAlias=resourcesProperties.getProperty('em.wsmKeyStore.signAlias')
       signAliasPassword=resourcesProperties.getProperty('em.wsmKeyStore.signAliasPassword')
       cryptAlias=resourcesProperties.getProperty('em.wsmKeyStore.cryptAlias')
       cryptAliasPassword=resourcesProperties.getProperty('em.wsmKeyStore.cryptAliasPassword')
    
       if keyStoreType is None or len(keyStoreType)==0:
         log.info('Keystore type is not provide for Oracle Web Service Manager, skipping. ')
       else:
         if keyStoreType == 'JKS':
            configureWSMKeystore(wsmDomain, keystoreType=keyStoreType, keystorePassword=keyStorePassword, location=keyStorePath, signAlias=signAlias, signAliasPassword=signAliasPassword, cryptAlias=cryptAlias, cryptAliasPassword=cryptAliasPassword) 
         else:
            log.error('Only Java keystore type is supported for Web Service Manager') 
    except Exception, error:
       log.error('Unable to configure web service manager domain' + str(error))
    else:
       log.info('Configure web service manager domain completed')  

def configure_system_policies(resourcesProperties, domainProperties):
    log.info('Configure system policies for enterprise manager')
    permissions=resourcesProperties.getProperty('em.permissions')
    if permissions is None or len(permissions)==0:
       log.info('Enterprise manager permssions is not specified, skipping. ')
    else:
       permissionList=permissions.split(',')
       for permission in permissionList:
           __configure_system_policy(permission, resourcesProperties, domainProperties)

def __configure_system_policy(permission, resourcesProperties, domainProperties):
    log.info('Configure system policy for enterprise manager with the permission name: ' + permission)
    try:
       codeBaseURL=resourcesProperties.getProperty('em.permission.' + str(permission) + '.codeBaseURL')
       codeBaseURL=codeBaseURL.replace('\\', '')
       permissionClass=resourcesProperties.getProperty('em.permission.' + str(permission) + '.permissionClass')
       permissionActions=resourcesProperties.getProperty('em.permission.' + str(permission) + '.permissionActions')
       permissionTarget=resourcesProperties.getProperty('em.permission.' + str(permission) + '.permissionTarget')
       grantPermission(codeBaseURL=codeBaseURL,permClass=permissionClass,permActions=permissionActions,permTarget=permissionTarget)
    except Exception, error:
       log.error('Unable to configure system policy for enterprise manager with the permission name ' + permission + ':' + str(error))
    else:
       log.info('Configure system policy for enterprise manager with the permission name ' + permission)

def configure_credentials(resourcesProperties, domainProperties):
    credentials=resourcesProperties.getProperty('em.credentials')
    if credentials is None or len(credentials)==0:
       log.info('Enterprise manager credentials is not specified, skipping.') 
    else:
       credentialList=credentials.split(',') 
       for credential in credentialList:
          __configure_credential(credential, resourcesProperties, domainProperties)  

def __configure_credential(credential, resourcesProperties, domainProperties):
    log.info('configure credential for enterprise manager with credential ' + credential)
    try:
       credentialKey=resourcesProperties.getProperty('em.credential.' + str(credential) + '.key')
       credentialMap=resourcesProperties.getProperty('em.credential.' + str(credential) + '.map')
       credentialUsername=resourcesProperties.getProperty('em.credential.' + str(credential) + '.username')
       credentialPassword=resourcesProperties.getProperty('em.credential.' + str(credential) + '.password')
       updateCred(map=credentialMap,key=credentialKey,user=credentialUsername,password=credentialPassword)
    except Exception, error:
       log.error('Unable to configure credential for enterprise manager with credential ' + credential + ':' + str(error))
    else:
       log.info('Configure credential for enterprise manager with the credential ' + credential)


