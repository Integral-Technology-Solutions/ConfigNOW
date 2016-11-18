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

def getPassword(domainProperties, propertyName, msg):
	error=0
	
	password=domainProperties.getProperty(propertyName)
	prompt=domainProperties.getProperty('password.prompt')
	
	if password is None or len(password)==0:
		if prompt:
			if  not password:
				dont_match=1
				while dont_match:
					print 'Please enter ' + msg + ': '
					password1=raw_input()
					print 'Confirm ' + msg + ': ' 
					password2=raw_input()
					if password1==password2:
						dont_match=0
					else:
						print 'PASSWORDS DO NOT MATCH'
				domainProperties.setProperty(propertyName,password1)    
		else:
			log.error('Please verify ' + propertyName + ' property exists in configuration.')
			error=1
	else:
		log.debug(propertyName + ' property is valid.')
        
	if error:
		sys.exit()
        