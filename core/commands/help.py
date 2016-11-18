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

from org.apache.tools.ant import Project, ProjectHelper

CORE_CMD_PATH='core/commands'
CORE_ANT_PATH='core/commands/ant'
CUSTOM_CMD_PATH='custom/commands'
CUSTOM_ANT_PATH='custom/commands/ant'

def run():

    if site_home:
        custom_cmd_path=site_home + '/' + CUSTOM_CMD_PATH
        custom_ant_path=site_home + '/' + CUSTOM_ANT_PATH
    else:
        custom_cmd_path=CUSTOM_CMD_PATH
        custom_ant_path=CUSTOM_ANT_PATH
        
    cmdDisp=CmdDisplayer()
    original_stdout = sys.stdout
    sys.stdout = NullDevice()
    if os.path.exists(CORE_CMD_PATH):
        for file in os.listdir(CORE_CMD_PATH):
            processFile(cmdDisp, CORE_CMD_PATH, file)
    if os.path.exists(custom_cmd_path):
        for file in os.listdir(custom_cmd_path):
            processFile(cmdDisp, custom_cmd_path, file)
    sys.stdout = original_stdout
    if os.path.exists(CORE_ANT_PATH):
        for file in os.listdir(CORE_ANT_PATH):
            processAntFile(cmdDisp, file, CORE_ANT_PATH)
    if os.path.exists(custom_ant_path):
        for file in os.listdir(custom_ant_path):
            processAntFile(cmdDisp, file, custom_ant_path)
    cmdDisp.display()
    
def processFile(cmdDisp, cmd_dir, file):
    name,ext=os.path.splitext(file)
    if ext == '.py':
        try:
            log.debug('Checking jython command ' + str(name) + ' for __doc__ information')
            mod = {}
            cmd_file = os.path.join(cmd_dir, file)
            execfile(cmd_file, globals(), mod)
            if mod['run']:
                description = mod['run'].__doc__
                if description is not None:
                    cmdDisp.addCmd(name, str(description))
            
        except Exception,ex:
            log.debug('Command ' + cmd_file + ' could not be processed: ' + str(sys.exc_info()[1]))
            

def processAntFile(cmdDisp, file, dir):
    name,ext=os.path.splitext(file)
    if ext == '.xml':
        try:
            log.debug('Checking ant build file ' + str(file) + ' for available targets')
            build_file = File(dir + '/' + file)
            project = Project()
            project.setUserProperty('ant.file', build_file.getAbsolutePath())
            project.init()
            helper = ProjectHelper.getProjectHelper()
            project.setProperty('ConfigNOW.home',os.getcwd())
            project.addReference('ant.projectHelper', helper)
            helper.parse(project, build_file)
            targets = project.getTargets()
            enum = targets.keys();
            while enum.hasMoreElements():
                target = enum.nextElement()
                value = targets.get(target)
                description = value.getDescription()
                if description is not None:
                    cmdDisp.addCmd(target, description)
        except:
            log.error('Ant build file ' + str(file) + ' could not be processed due to: ' + str(sys.exc_info()[0]))
            log.info('Suggested fix: ' + str(sys.exc_info()[1]))
                
class CmdDisplayer:

    def __init__(self):
        self.longest_cmd=0
        self.cmd_desc = []
    
    def addCmd(self, cmd, description):
        if len(cmd) > self.longest_cmd:
            self.longest_cmd=len(cmd)
        self.cmd_desc.append([cmd,description])
        
    def display(self): 
        print '\nAvailable commands are:\n'
        self.cmd_desc.sort()
        for cmd in self.cmd_desc:
            print ' ' + self.trailCmd(cmd[0]) + '  ' + cmd[1]
        print '\n'
        
    def trailCmd(self, cmd):
        trailing = self.longest_cmd - len(cmd)
        returnString = cmd
        for i in range(0, trailing):
            returnString+=' '
        return returnString
        
class NullDevice:
    def write(self, s):
        pass
