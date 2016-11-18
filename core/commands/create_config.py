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

from java.io import BufferedReader, FileReader, BufferedWriter, FileWriter

import re

def run():
    print
    base = raw_input('Base file, eg. config/templates/wl_as_template.properties? ')
    env = raw_input('Environment, eg. local? ')
    print
    new_cfg = 'config/' + env + '/new_config.properties'
    input = BufferedReader(FileReader(base))
    output = BufferedWriter(FileWriter(new_cfg))
    output.write('base=' + base + '\n\n')
    line = input.readLine()
    while line is not None:
        if re.match('.*\?', line):
            output.write(line)
            output.newLine()
        line = input.readLine()
    input.close()
    output.close()
    log.info('new configuration file written to: ' + new_cfg)
