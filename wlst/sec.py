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
## sec.py
##
## This script contains functions that manipulate Security.

try:
	from weblogic.management.security.authentication import UserEditorMBean
except ImportError:
	UserEditorMBean = None


#=======================================================================================
# Load required modules
#=======================================================================================

try:
    commonModule
except NameError:
    execfile('wlst/common.py')

def createUser(username, password, description, authenticator):
    log.info("Creating a user : " + str(username) + ". Authenticator is " + str(authenticator))
    atnr=cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider(str(authenticator))
    atnr.createUser(username,password,description)
    print "Created user successfully"
    
def addUserToGroup(username,groupname,authenticator):
    log.info("Adding a user : " + str(username) + " to group " + groupname + ". Authenticator is " + str(authenticator))
    atnr=cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider(str(authenticator))
    atnr.addMemberToGroup(groupname,username)
    log.info("Done adding a user")

def createGroup(groupname, description, authenticator):
    log.info("Creating a group : " + str(groupname) + " with a description of " + str(description) + ". Authenticator is " + str(authenticator))
    atnr=cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider(str(authenticator))
    if int(atnr.groupExists(groupname)) == 0:
    	atnr.createGroup(groupname,description)
    	log.info("Created group successfully")

def removeUser(username, authenticator):
    log.info("Removing user : " + str(username) + ". Authenticator is " + str(authenticator))
    atnr=cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider(str(authenticator))
    if int(atnr.userExists(username)) == 1:
    	atnr.removeUser(username)
    	log.info("Removed user successfully")

#==============================================================================
# createUsers
#
# Creates all additional users configured in properties file.
#==============================================================================
def createUsers(resourcesProperties, domainProperties):
	allUsers = resourcesProperties.getProperty('security.users')
	if not allUsers is None and len(allUsers) > 0:
		userList = allUsers.split(',')
		for newUser in userList:
			userPrefix = 'security.user.' + newUser + '.'
			userName = resourcesProperties.getProperty(userPrefix + 'username')
			userPassword = resourcesProperties.getProperty(userPrefix + 'password')
			userDescription = resourcesProperties.getProperty(userPrefix + 'description')
			authenticator = resourcesProperties.getProperty(userPrefix + 'authenticator')
			if not authenticator is None:
				createUser(userName, userPassword, userDescription, authenticator)
			else:
				createUser(userName, userPassword, userDescription, 'DefaultAuthenticator')