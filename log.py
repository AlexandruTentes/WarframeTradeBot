import singleton
import utility
import globals

severity_level = [" ", " LOG: ", " WARNING: ", " ERROR: ", " FATAL: "]

class SEVERITY():
    NONE = 0
    WEAK = 1
    EASY = 2
    HARD = 3
    FATAL = 4
    
class Logger(metaclass=singleton.Singleton):    
    file = None
    util = None
    global_data = None

    def __init__(self):
        self.util = utility.Utility()
        self.global_data = globals.Globals()

    def open_log_file(self, path = None):
        if path == None:
            return
        
        time_now = self.util.get_time()[0].replace('/', '_')
        path = path + "." + time_now + ".txt"
        
        try:
            print("Attempting to open the log file... (" + path + ")")
            self.file = open(path, 'a+')
            print("Log file loaded successfully!")
            
        except:
            self.log(SEVERITY.HARD, "Could not open file at path '" + path + "'!")

    def log_cmd(self, severity, message, location):
        print("\n[" + self.util.get_time()[1] + "]" + severity_level[severity] + "\t" + message + "\n\t\t" + location)

    def log_file(self, severity, message, location):
        if self.file == None:
            self.log_cmd(severity, message, location)
            return 1

        try:
            self.file.write("\n[" + self.util.get_time()[1] + "]" + severity_level[severity] + "\t" + message + "\n\t\t" + location)

        except:
            self.file.close()
            self.log(SEVERITY.HARD, "Could not write to file!")
            self.log(severity, message)

        return 0

    def log(self, severity, message, err = None):
        self.open_log_file(self.global_data.log_path)
        
        filename, lineno = self.util.get_codeline()
        reason = ""
        location = "\tError thrown inside '" + filename + "' on line " + str(lineno) + "\n"

        if err != None: reason = "\n\t\t\tReason: " + str(err)
        flag = self.log_file(severity, message + reason, location)
        if flag == 0: self.log_cmd(severity, message + reason, location)

        if severity == SEVERITY.FATAL:
            self.global_data.program_running = False
            self.clear(False)
        
    def clear(self, flag = True):
        if flag:
            print("\t\t-clearing LOG data from memory...")
            
        if self.file != None:
            self.file.close()
