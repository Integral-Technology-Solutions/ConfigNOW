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
    """This is the command used to configure webloic security providers """
    log.debug('-- in configure_security_provider.py')

    # Assert the input configurations
    assertions.sanityCheckInstall(config)
    assertions.sanityCheckDomainConfig(config)
    assertions.sanityCheckOnlineConfig(config)
    hasExceptions = false

    # Configure the security provider
    try:
        __connectAdminServer(config)
        edit()
        log.info('Start edits')
        startEdit()
        configureAuthenticationProviders(config)
        sortAuthenticationProviders(config)
        configureCredentialMappers(config)
        log.info('Save the current changes')
        save()
        log.info('Activate the current changes')
        activate()

    except Exception, error:
        log.error('Unable to configure authentication provider ' + str(error))
        dumpStack()
        cancelEdit('y')
        hasExceptions = true
    else:
        log.info('exit the current session')
        disconnect('true')
        exit()

def sortAuthenticationProviders(config):
    log.info('Start sorting authentication providers')
    navigateToDefaultSecurityRealm(config)
    cd('AuthenticationProviders')

    authenticationProviderArray = []
    authenticationProviders = config.getProperty('securityConfiguration.authenticationProviders.sortOrder')
    authenticationProviderList = authenticationProviders.split(',')

    for authenticationProvider in authenticationProviderList:
        log.info('Add ' + authenticationProvider + ' to the Authentication Providers')
        authenticationProviderObject = ObjectName('Security:Name=myrealm' + authenticationProvider)
        authenticationProviderArray.append(authenticationProviderObject)

    set('AuthenticationProviders',jarray.array(authenticationProviderArray, ObjectName))
    log.info('Successfully sort the authentication providers')

def navigateToDefaultSecurityRealm(config):
    domainName = config.getProperty('wls.domain.name')
    log.info('Navigate to /SecurityConfiguration/' + domainName + '/Realms/myrealm')
    cd('/SecurityConfiguration/' + domainName + '/Realms/myrealm')

# Authentication Providers
def configureAuthenticationProviders(config):
    authenticationProviders = config.getProperty('securityConfiguration.authenticationProviders')
    authenticationProviderList = authenticationProviders.split(',')

    for authenticationProvider in authenticationProviderList:
        log.info('Configure authentication provider ' + authenticationProvider)
        configureAuthenticationProvider(config, authenticationProvider)

def isAuthenticationProviderExisted(config, authenticationProviderName):
    auth = getAuthenticationProvider(config, authenticationProviderName)

    if auth is None:
        log.info('Authentication Provider ' + authenticationProviderName + ' does not existed' )
        return false
    else:
        log.info('Authentication Provider ' + authenticationProviderName + ' existed' )
        return true

def getAuthenticationProvider(config, authenticationProviderName):
    navigateToDefaultSecurityRealm(config)
    return cmo.lookupAuthenticationProvider(authenticationProviderName)

def createAuthenticationProvider(config, authenticationProviderType, authenticationProviderName):
    log.info('Create authentication provider ' + authenticationProviderName + ' with type ' + authenticationProviderType)
    navigateToDefaultSecurityRealm(config)

    if authenticationProviderType == 'authentication':
        cmo.createAuthenticationProvider(authenticationProviderName, 'weblogic.security.providers.authentication.ActiveDirectoryAuthenticator')
    elif authenticationProviderType == 'asserter':
        cmo.createAuthenticationProvider(authenticationProviderName, 'weblogic.security.providers.saml.SAMLIdentityAsserterV2')

    log.info('Successfully create authentication provider ' + authenticationProviderName + ' with type ' + authenticationProviderType)

def deleteAuthenticationProvider(config, authenticationProviderName):
    log.info('Delete authentication provider ' + authenticationProviderName)
    auth = getAuthenticationProvider(config, authenticationProviderName)
    cmo.destroyAuthenticationProvider(auth)
    log.info('Successfully delete authentication provider ' + authenticationProviderName)

def configureAuthenticationProvider(config, authenticationProvider):
    log.info('Configure authentication provider ' + authenticationProvider)

    authenticationProviderName = config.getProperty('authenticationProvider.' + authenticationProvider + '.name')
    authenticationProviderType = config.getProperty('authenticationProvider.' + authenticationProvider + '.type')

    if isAuthenticationProviderExisted(config, authenticationProviderName):
        deleteAuthenticationProvider(config, authenticationProviderName)

    createAuthenticationProvider(config, authenticationProviderType, authenticationProviderName)
    navigateToDefaultSecurityRealm(config)
    cd('AuthenticationProviders')
    cd(authenticationProviderName)

    # Connection
    if authenticationProviderType == 'authentication':
        cmo.setControlFlag(config.getProperty('authenticationProvider.' + authenticationProvider + '.controlFlag'))
        cmo.setHost(config.getProperty('authenticationProvider.' + authenticationProvider + '.host'))
        cmo.setPort(int(config.getProperty('authenticationProvider.' + authenticationProvider + '.port')))
        cmo.setPrincipal(config.getProperty('authenticationProvider.' + authenticationProvider + '.principal'))
        cmo.setSSLEnabled(bool(config.getProperty('authenticationProvider.' + authenticationProvider + '.sslEnabled')))
        cmo.setGuidAttribute(config.getProperty('authenticationProvider.' + authenticationProvider + '.guidAttribute'))
        cmo.setPropagateCauseForLoginException(bool(config.getProperty('authenticationProvider.' + authenticationProvider + '.propagateCauseForLoginException')))

        # Users
        cmo.setUserBaseDN(config.getProperty('authenticationProvider.' + authenticationProvider + '.userBaseDN'))
        cmo.setAllUsersFilter(config.getProperty('authenticationProvider.' + authenticationProvider + '.allUsersFilter'))
        cmo.setUserFromNameFilter(config.getProperty('authenticationProvider.' + authenticationProvider + '.userFromNameFilter'))
        cmo.setUserNameAttribute(config.getProperty('authenticationProvider.' + authenticationProvider + '.userNameAttribute'))
        cmo.setUserObjectClass(config.getProperty('authenticationProvider.' + authenticationProvider + '.userObjectClass'))

        #Group
        cmo.setGroupBaseDN(config.getProperty('authenticationProvider.' + authenticationProvider + '.groupBaseDN'))
        cmo.setAllGroupsFilter(config.getProperty('authenticationProvider.' + authenticationProvider + '.allGroupsFilter'))
        cmo.setGroupFromNameFilter(config.getProperty('authenticationProvider.' + authenticationProvider + '.groupFromNameFilter'))
        cmo.setGroupSearchScope(config.getProperty('authenticationProvider.' + authenticationProvider + '.groupSearchScope'))
        cmo.setGroupMembershipSearching(config.getProperty('authenticationProvider.' + authenticationProvider + '.groupMembershipSearching'))
        cmo.setMaxGroupMembershipSearchLevel(int(config.getProperty('authenticationProvider.' + authenticationProvider + '.maxGroupMembershipSearchLevel')))
        cmo.setStaticGroupDNsfromMemberDNFilter(config.getProperty('authenticationProvider.' + authenticationProvider + '.staticGroupDNsfromMemberDNFilter'))

    elif authenticationProviderType == 'asserter':
        cmo.setIdentityDomain(config.getProperty('authenticationProvider.' + authenticationProvider + '.identityDomain'))

    log.info('Successfully configure authentication provider ' + authenticationProvider)

def getAuthenticationProviderPropertyValue(config, authenticationProviderName, propertyName):
    return config.getProperty('authenticationProvider.' + authenticationProviderName + '.' + propertyName)

# Credential Mapper
def getCredentialMapper(config, credentialMapperName):
    navigateToDefaultSecurityRealm(config)
    return cmo.lookupCredentialMapper(credentialMapperName)

def isCredentialMapperExisted(config, credentialMapperName):
    credentialMapper = getCredentialMapper(config, credentialMapperName)

    if credentialMapper is None:
        log.info('Credential mapper ' + credentialMapperName + ' does not existed' )
        return false
    else:
        log.info('Credential mapper ' + credentialMapperName + ' existed' )
        return true

def configureCredentialMappers(config):
    credentialMappers = config.getProperty('securityConfiguration.credentialMappers')
    credentialMapperList = credentialMappers.split(',')

    for credentialMapper in credentialMapperList:
        log.info('Configure credential mapper ' + credentialMapper)
        configureCredentialMapper(config, credentialMapper)

def createCredentialMapper(config, credentialMapperType, credentialMapperName):
    log.info('Create credential mapping ' + credentialMapperName + ' with type ' + credentialMapperType)
    navigateToDefaultSecurityRealm(config)

    if credentialMapperType == 'PKI':
        cmo.createCredentialMapper(credentialMapperName, 'weblogic.security.providers.credentials.PKICredentialMapper')
    elif credentialMapperType == 'SAML':
        cmo.createCredentialMapper(credentialMapperName, 'weblogic.security.providers.saml.SAMLCredentialMapperV2')

    log.info('Successfully create credential mapping ' + credentialMapperName + ' with type ' + credentialMapperType)

def deleteCredentialMapper(config, credentialMapperName):
    log.info('Delete credential mapper ' + credentialMapperName)
    credentialMapper = getCredentialMapper(config, credentialMapperName)
    cmo.destroyCredentialMapper(credentialMapper)
    log.info('Successfully delete credential mapper ' + credentialMapperName)

def configureCredentialMapper(config, credentialMapper):
    log.info('Configure credential mapper ' + credentialMapper)

    credentialMapperName = config.getProperty('credentialMapper.' + credentialMapper + '.name')
    credentialMapperType = config.getProperty('credentialMapper.' + credentialMapper + '.type')

    if isCredentialMapperExisted(config, credentialMapperName):
        deleteCredentialMapper(config, credentialMapperName)

    createCredentialMapper(config, credentialMapperType, credentialMapperName)
    navigateToDefaultSecurityRealm(config)
    cd('CredentialMappers')
    cd(credentialMapperName)

    if credentialMapperType == 'SAML':
        cmo.setIssuerURI(config.getProperty('credentialMapper.' + credentialMapper + '.issuerURI'))
        cmo.setDefaultTimeToLive(int(config.getProperty('credentialMapper.' + credentialMapper + '.defaultTimeToLive')))
        cmo.setSigningKeyAlias(config.getProperty('credentialMapper.' + credentialMapper + '.signingKeyAlias'))
        cmo.setSigningKeyPassPhrase(config.getProperty('credentialMapper.' + credentialMapper + '.signingKeyPassPhrase'))

