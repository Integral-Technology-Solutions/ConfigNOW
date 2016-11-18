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

import getopt, sys, os
from java.io import FileInputStream
from java.io import File
from jarray import zeros,array

try:
	from weblogic.management.security.authentication import AuthenticationProviderMBean
except ImportError:
	AuthenticationProviderMBean = None

###==============================================================================
###
#    securityProviders.py
#    Author: Craig Barr
###
###==============================================================================
# 
# This script configures a security provider (e.g. Active Directory)
#
###==============================================================================

# Supported Authenticators
ACTIVE_DIRECTORY_AUTHENTICATOR = 'ActiveDirectoryAuthenticator'
NOVELL_AUTHENTICATOR = 'NovellAuthenticator'

TRUE = 1
FALSE = 0

#=======================================================================================
# Import common library
#=======================================================================================

try:
	commonModule
except NameError:
	execfile('wlst/common.py')
	
def createSecurityProviders(resourcesProperties, domainProperties):
	
	authenticationProviders=resourcesProperties.getProperty('security.providers')
	
	if authenticationProviders is None or len(authenticationProviders)==0:
		log.info('No security providers specified, skipping.')
	else:
		defaultRealm = cmo.getSecurityConfiguration().getDefaultRealm()

		initialAuthProviders = defaultRealm.getAuthenticationProviders()
		
		newAuthProvidersList = []
				
		authenticationProvidersList = authenticationProviders.split(",")
		for authProvider in authenticationProvidersList:
		
			name=resourcesProperties.getProperty('security.provider.' + authProvider + '.name')
			type=resourcesProperties.getProperty('security.provider.' + authProvider + '.type')
			controlFlag=resourcesProperties.getProperty('security.provider.' + authProvider + '.controlFlag')
			userBaseDN=resourcesProperties.getProperty('security.provider.' + authProvider + '.userBaseDN')
			groupBaseDN=resourcesProperties.getProperty('security.provider.' + authProvider + '.groupBaseDN')
			principal=resourcesProperties.getProperty('security.provider.' + authProvider + '.principal')
			host=resourcesProperties.getProperty('security.provider.' + authProvider + '.host')
			credential=resourcesProperties.getProperty('security.provider.' + authProvider + '.credential')
			groupFromNameFilter=resourcesProperties.getProperty('security.provider.' + authProvider + '.groupFromNameFilter')
			staticGroupDNs=resourcesProperties.getProperty('security.provider.' + authProvider + '.staticGroupDNsfromMemberDNFilter')
			staticGroupObject=resourcesProperties.getProperty('security.provider.' + authProvider + '.staticGroupObjectClass')
		 	staticMember=resourcesProperties.getProperty('security.provider.' + authProvider + '.staticMemberDNAttribute')
		 	userFromNameFilter=resourcesProperties.getProperty('security.provider.' + authProvider + '.userFromNameFilter')
		 	userNameAttribute=resourcesProperties.getProperty('security.provider.' + authProvider + '.userNameAttribute')
		 	userObjectClass=resourcesProperties.getProperty('security.provider.' + authProvider + '.userObjectClass')
		 	useTokenGroup=resourcesProperties.getProperty('security.provider.' + authProvider + '.useTokenGroupsForGroupMembershipLookup')
		 	port=resourcesProperties.getProperty('security.provider.' + authProvider + '.port')
		 	
			if not name is None:
			
				if type==ACTIVE_DIRECTORY_AUTHENTICATOR or type==NOVELL_AUTHENTICATOR:
					if type==ACTIVE_DIRECTORY_AUTHENTICATOR:
						auth = defaultRealm.createAuthenticationProvider(name, 'weblogic.security.providers.authentication.ActiveDirectoryAuthenticator')
						if not useTokenGroup is None and useTokenGroup.upper()=='TRUE':
							adAuth.setUseTokenGroupsForGroupMembershipLookup(TRUE)
					elif type==NOVELL_AUTHENTICATOR:
						auth = defaultRealm.createAuthenticationProvider(name, 'weblogic.security.providers.authentication.NovellAuthenticator')
			
					if not controlFlag is None:
						auth.setControlFlag(controlFlag)
					if not userBaseDN is None:
						auth.setUserBaseDN(userBaseDN)
					if not groupBaseDN is None:
						auth.setGroupBaseDN(groupBaseDN)
					if not principal is None:
						auth.setPrincipal(principal)
					if not host is None:
						auth.setHost(host)
					if not credential is None:
						auth.setCredential(credential)
					if not groupFromNameFilter is None:
						auth.setGroupFromNameFilter(groupFromNameFilter)
					if not staticGroupDNs is None:
						auth.setStaticGroupDNsfromMemberDNFilter(staticGroupDNs)
					if not staticGroupObject is None:
						auth.setStaticGroupObjectClass(staticGroupObject)
					if not staticMember is None:
						auth.setStaticMemberDNAttribute(staticMember)
					if not userFromNameFilter is None:
						auth.setUserFromNameFilter(userFromNameFilter)
					if not userNameAttribute is None:
						auth.setUserNameAttribute(userNameAttribute)
					if not userObjectClass is None:
						auth.setUserObjectClass(userObjectClass)
					if not port is None:
						auth.setPort(int(port))
					newAuthProvidersList.append(auth)
		
		# Re-order the authentication providers so that the new ones are at the start
		
		initialAuthSize=initialAuthProviders.__len__()
		newAuthSize=newAuthProvidersList.__len__()
		authSize=initialAuthSize + newAuthSize
				
		authProviders = zeros(authSize, AuthenticationProviderMBean)
		
		i = 0
		for auth in newAuthProvidersList:
			authProviders[i] = auth
			i = i + 1
		
		for initialAuth in initialAuthProviders:
			authProviders[i] = initialAuth
			i = i + 1
		
		defaultRealm.setAuthenticationProviders(authProviders)
		