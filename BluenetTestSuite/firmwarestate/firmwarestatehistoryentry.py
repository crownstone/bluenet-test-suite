

class FirmwareStateHistoryEntry:
    """
    [[datetime.datetime.now(), ptr, classname, valuename, value]]
    """
    def __init__(self, time, ptr, classname, valuename, value):
        self.time = time
        self.ptr = ptr
        self.classname = classname
        self.valuename = valuename
        self.value = value

    def __str__(self):
        return "{0} {1} {2}.{3}={4}".format(
            self.time,
            self.ptr,
            self.classname,
            self.valuename,
            self.value
        )

    __repr__ = __str__
