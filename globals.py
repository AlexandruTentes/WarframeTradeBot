import singleton

class Globals(metaclass=singleton.Singleton):
    app_name = "Warframe Stock Market"
    log_path = "logs\\Log"
    config_path = "Configs"    
    program_running = True
