#This will just implament a call back to a function passed into INIT

class InvalidExtensionEnvironment(Exception):
    pass

class lockneoled:

    def __init__(self, sFun):
        self.SetLight = sFun

    # The below methods should be implemented by subclasses

    def during_bootup(self, keyboard):
        pass
        #raise NotImplementedError

    def before_matrix_scan(self, keyboard):
        pass
        #raise NotImplementedError

    def after_matrix_scan(self, keyboard):
        #Just do callback
        self.SetLight()
        pass
        #raise NotImplementedError

    def process_key(self, keyboard, key, is_pressed, int_coord):
        #worked in here
        return key

    def before_hid_send(self, keyboard):
        pass
        #raise NotImplementedError

    def after_hid_send(self, keyboard):
        pass
        #raise NotImplementedError

    def on_powersave_enable(self, keyboard):
        pass
        #raise NotImplementedError

    def on_powersave_disable(self, keyboard):
        pass
        #raise NotImplementedError

    def deinit(self, keyboard):        
        pass

