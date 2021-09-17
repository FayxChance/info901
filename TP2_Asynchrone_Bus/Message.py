class Message:
    def __init__(self, cpt, msg, dest):
        self.cpt = cpt
        self.msg = msg
        self.dest = dest

    def get_cpt(self):
        return self.cpt

    def get_msg(self):
        return self.msg
