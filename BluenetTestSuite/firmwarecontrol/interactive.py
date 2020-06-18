import time, inspect
from BluenetLib import Bluenet, BluenetEventBus, UsbTopics

from BluenetLib.lib.core.uart.UartTypes import UartTxType
from BluenetLib.lib.core.uart.UartWrapper import UartWrapper
from BluenetLib.lib.core.uart.uartPackets import UartPacket
from BluenetLib.lib.protocol.BlePackets import ControlPacket
from BluenetLib.lib.protocol.BluenetTypes import ControlType
from BluenetLib.lib.topics.SystemTopics import SystemTopics
from BluenetLib.lib.util.Conversion import Conversion

import pygame #for nice keyboard input

"""
Note: this file predates the test framework. It contains some useful code which is likely better
off to be ported over into a jupyter notebook for interactive firmware manipulation as a means for 
supervised testing. This hasn't been done yet, but see pivotal for the ticket #173401664.
"""

def printFunctionName():
    print(inspect.currentframe().f_back.f_code.co_name)

def sendToCrownstone(commandtype, packetcontent):
    """
    [commandtype] must be an element of the ControlType enum.
    """
    controlPacket = ControlPacket(commandtype)
    controlPacket.appendByteArray(packetcontent)

    uartPacket = UartWrapper(UartTxType.CONTROL, controlPacket.getPacket()).getPacket()

    BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)

def propagateEventToCrownstone(eventtype, eventdata):
    payload = []
    payload += Conversion.uint16_to_uint8_array(eventtype)
    payload += eventdata

    uartPacket = UartWrapper(UartTxType.MOCK_INTERNAL_EVT, payload).getPacket()
    BluenetEventBus.emit(SystemTopics.uartWriteData, uartPacket)

def WhatToDoWithUartData(data):
    #print(".")
    pass  # already handled somehwere else apparently

# ================================= Packet definitions =================================
class TimeOfDay:
    def __init__(self, offset = 0):
        self.baseTime = 0 # ofset from midnight
        self.offset = offset

    def hms(self, h,m,s):
        self.offset = s + 60 * (m + 60*h)
        return self

    def SunRise(offset = 0):
        t = TimeOfDay(offset)
        t.baseTime = 1
        return t

    def SunSet(offset = 0):
        t = TimeOfDay(offset)
        t.baseTime = 2
        return t

    def serialize(self):
        result = []
        result += Conversion.uint8_to_uint8_array(self.baseTime)
        result += Conversion.uint32_to_uint8_array(self.offset)
        return result

    def toString(self):
        return "TimeOfDay({0} {1})".format(self.baseTime, self.offset)

class PresenceCondition:
    def __init__(self, typ, activeRoomsMask, timeout):
        self.typ = typ
        self.activeRoomsMask = activeRoomsMask
        self.timeout = timeout

    def serialize(self):
        result = []
        result += Conversion.uint8_to_uint8_array(self.typ)
        result += [ self.activeRoomsMask >> 8*i & 0xFF for i in range(8)[::1] ]
        # result += Conversion.uint64_to_uint8_array(self.activeRoomsMask)
        result += Conversion.uint32_to_uint8_array(self.timeout)

        return result

    def toString(self):
        return "PresenceCondition({0} {1} {2})".format(self.typ, hex(self.activeRoomsMask), self.timeout)

class Behaviour:
    def __init__(self, intensity, activeDays, activeFrom, activeUntil):
        # self.typ needs to be set in child class.
        self.typ = None
        self.intensity = intensity
        self.profileId = 0
        self.activeDays = activeDays
        self.activeFrom = activeFrom
        self.activeUntil = activeUntil

    def serialize(self):
        result = []
        result += Conversion.uint8_to_uint8_array(self.typ)
        result += Conversion.uint8_to_uint8_array(self.intensity)
        result += Conversion.uint8_to_uint8_array(self.profileId)
        result += Conversion.uint8_to_uint8_array(self.activeDays)
        result += self.activeFrom .serialize()
        result += self.activeUntil.serialize()
        return result

    def toString(self):
        return "Behaviour({0} {1} {2} {3} {4} {5} )".format(
            self.typ, 
            self.intensity, 
            self.profileId,
            self.activeDays, 
            self.activeFrom.toString(),
            self.activeUntil.toString())

class SwitchBehaviour(Behaviour):
    def __init__(self, intensity, activeDays, activeFrom, activeUntil, presenceCondition):
        super().__init__(intensity, activeDays, activeFrom, activeUntil)
        self.typ = 0 # see BEHAVIOUR.md
        self.presenceCondition = presenceCondition

        __class__.behaviourIntensityCounter += 1
        __class__.behaviourIntensityCounter %= 100

    def serialize(self):
        print("serializing " + self.toString())
        return super().serialize() + self.presenceCondition.serialize()

    def toString(self):
        return "SwitchBehaviour({0} {1})".format(super().toString(),self.presenceCondition.toString())

    # used to give subsequently by example() created behaviours a 
    # different intensity for debugging
    behaviourIntensityCounter = 1
   
    @staticmethod
    def example():
        """Generates an example behaviour object with some arbitrary presets """
        return SwitchBehaviour(
            SwitchBehaviour.behaviourIntensityCounter,
            0b01010101,
            TimeOfDay().hms(23, 0,0),
            TimeOfDay().hms(23,30,0),
            PresenceCondition(
                1,
                0xffff0000ffff0000,
                5 # seconds grace period
            )
        )

class TwilightBehaviour(Behaviour):
    def __init__(self, intensity, activeDays, activeFrom, activeUntil):
        super().__init__(intensity, activeDays, activeFrom, activeUntil)
        self.typ = 1 # see BEHAVIOUR.md

    def serialize(self):
        print("serializing " + self.toString())
        return super().serialize()

    def toString(self):
        return "TwilightBehaviour({0})".format(super().toString())

class ExtendedSwitchBehaviour(SwitchBehaviour):
    def __init__(self, intensity, activeDays, activeFrom, activeUntil, presenceCondition, extensionCondition):
        super().__init__(intensity, activeDays, activeFrom, activeUntil,presenceCondition)

        self.typ = 2 # see BEHAVIOUR.md
        self.extensionCondition = extensionCondition

    def serialize(self):
        print("serializing " + self.toString())
        return super().serialize() + self.extensionCondition.serialize()

    def toString(self):
        return "ExtendedSwitchBehaviour({0} {1})".format(super().toString(),self.extensionCondition.toString())

class BehaviourEntry:
    def __init__(self, index, behaviour):
        self.index = index
        self.behaviour = behaviour

    def serialize(self):
        result = []
        result += Conversion.uint8_to_uint8_array(self.index)
        result += self.behaviour.serialize()
        return result

# ================================= Behaviour related functions =================================
def saveBehaviour(behave):
    printFunctionName()
    sendToCrownstone(ControlType.SAVE_BEHAVIOUR, behave.serialize())
    print("behaviour sent")

def replaceBehaviour(index, behave):
    printFunctionName()
    bh_entry = BehaviourEntry(index, behave)
    sendToCrownstone(ControlType.REPLACE_BEHAVIOUR, bh_entry.serialize())

def getBehaviourIndices():
    printFunctionName()
    sendToCrownstone(ControlType.GET_BEHAVIOUR_INDICES, [])

def deleteBehaviour(index):
    printFunctionName()
    sendToCrownstone(ControlType.REMOVE_BEHAVIOUR, [index])

def getBehaviour(index):
    printFunctionName()
    sendToCrownstone(ControlType.GET_BEHAVIOUR, [index])

def setBehaviourHandlerActive(isactive):
    printFunctionName()
    sendToCrownstone(ControlType.BEHAVIOURHANDLER_SETTINGS, [0x01 if isactive else 0x00])

def setTwilight(intensity):
    saveBehaviour(
        TwilightBehaviour(
            intensity, 0b11111111,
            TimeOfDay.SunRise(60*60), # sunrise plus 1h  #TimeOfDay().hms(9,0,0),
            TimeOfDay.SunSet(-60*60) # sunset minus 1h   #TimeOfDay().hms(20,0,0)
        )
    )

def setExtendedBehaviour(timeout):
    """
    smart timer, duration 60 seconds, starting 60 seconds from now, with given timeout
    """
    saveBehaviour(
        ExtendedSwitchBehaviour(
                100, 0b11111111, #intensity, weekdays
                TimeOfDay(currentTimeSecSinceMidnight() + 1*30),
                TimeOfDay(currentTimeSecSinceMidnight() + 2*30),
                PresenceCondition(0, 0x00, timeout), # VacuouslyTrue, rooms, timeout
                PresenceCondition(3, 0xff, timeout) # AnyoneInSphere, rooms, timeout
            )
    )

# ================================= Lower level functions =================================
def switch(value):
    printFunctionName()
    if value > 90:
        sendToCrownstone(ControlType.SWITCH, [255]) # dummy to test translucent override with
    sendToCrownstone(ControlType.SWITCH, [value])

def setAllowDimming(value):
    printFunctionName()
    sendToCrownstone(ControlType.ALLOW_DIMMING, [1 if value else 0])

def setLocked(value):
    printFunctionName()
    sendToCrownstone(ControlType.LOCK_SWITCH, [1 if value else 0])

def currentTimeSecSinceMidnight():
    t = time.localtime()
    return int(t.tm_sec + 60*t.tm_min + 60*60 * t.tm_hour)

def setTimeSecSinceMidnight(ssm):
    """expects an uint32"""
    timetoset_gmtime = time.gmtime(ssm)

    print("set time " + str(timetoset_gmtime.tm_hour) + ":" + str(timetoset_gmtime.tm_min) + ":" + str( timetoset_gmtime.tm_sec))
    sendToCrownstone(ControlType.SET_TIME,Conversion.uint32_to_uint8_array(ssm))

def setTime(value):
    """value interpreted in 'half hours after todays midnight starting at 00:30"""
    now_epoch = time.time()
    now_gmtime = time.gmtime(now_epoch)
    midnight_epoch = now_epoch - (now_gmtime.tm_sec + 60* (now_gmtime.tm_min + 60 * now_gmtime.tm_hour))
   
    now_epoch = int(now_epoch)
    midnight_epoch_int = int(midnight_epoch)
    timetoset_int = midnight_epoch_int + (60*30)*(1+value)

    setTimeSecSinceMidnight(timetoset_int)

def setSunTime(value):
    """Set sunrise/sunset value"""
    v = []
    v += Conversion.uint32_to_uint8_array(value * 60 * 60)
    v += Conversion.uint32_to_uint8_array( (24 - value) * 60 * 60)
    sendToCrownstone(ControlType.SET_SUN_TIME,v)

def sendPresence(room, profileId):
    # injects a background message that indicates a
    # nearby user. Warning: fragile mockup. May interfere with tap to toggle if 'flags' is set incorrectly.
    print("send presence of id %d in room %d" % (profileId,room))
    propagateEventToCrownstone(
        256+0,
        Conversion.uint8_to_uint8_array(0) + # ? uint8_t  protocol;
        Conversion.uint8_to_uint8_array(1) + #   uint8_t  sphereId;
        Conversion.uint32_to_uint8_array(0) + # ! uint8_t* macAddress;
        Conversion.uint8_to_uint8_array(0) + # ? int8_t   adjustedRssi;
        Conversion.uint8_to_uint8_array(room) + #   uint8_t  locationId;
        Conversion.uint8_to_uint8_array(profileId) + #   uint8_t  profileId;
        Conversion.uint8_to_uint8_array(0)   # ! uint8_t  flags;
    )

def gotoDfu():
    """
    Sends uart command to put device in dfu mode.
    """
    printFunctionName()
    sendToCrownstone(ControlType.GOTO_DFU, [])

# ================================= Test scenarios =================================
def testScenario_0():
    """
    No presence rules, 
    active all days, 
    trivial conflict between 02:00 and 03:00
    non trivial conflict between 03:00 and 04:00

    intensity         99      99      50  
                [ ---- b1 ---- ][ ---- b3 ---- ]
                    [ ----- b2 ----- ]
    time  00:30 01:00  02:00  03:00  04:00  05:00  06:00  07:00  08:00
    index 0     1      3      5      7      9
    """
    return [
        SwitchBehaviour(
            100, 0b11111111,
            TimeOfDay().hms(1,0,0),
            TimeOfDay().hms(3,0,0),
            PresenceCondition(1, 0x00, 5)
        ),
        SwitchBehaviour(
            100, 0b11111111,
            TimeOfDay().hms(2,0,0),
            TimeOfDay().hms(4,0,0),
            PresenceCondition(1, 0x00, 5)
        ),
        SwitchBehaviour(
            50, 0b11111111,
            TimeOfDay().hms(3,0,0),
            TimeOfDay().hms(5,0,0),
            PresenceCondition(1, 0x00, 5)
        )
    ]

def testScenario_1():
    """
    all behaviours user 0, 
    no overlapping behaviours,
    time t corresponds to presence description type t.
    rooms mask 0x0f
    intensity distinct for all behaviours
    """
    return [
        SwitchBehaviour(
            99-i, 0b11111111,
            TimeOfDay().hms(i,0,0),
            TimeOfDay().hms(i+1,0,0),
            PresenceCondition(i, 0xae0000000000000f, 5)
        ) 
        for i in range(5)
    ]

def testScenario_2():
    """
    A few behaviours that have a 10 second interval starting from the current time for a quick sanity check
    """
    c = currentTimeSecSinceMidnight()
    interval = 10
    interval_2 = int(interval/2)
    return [
        SwitchBehaviour(
            99-11*i, 0b11111111,
            TimeOfDay(c + i*interval + 0),
            TimeOfDay(c + i*interval +interval_2),
            PresenceCondition(0, 0xffffffffffffffff, 5)
        ) 
        for i in range(10)
    ]

def SetupBehaviourTestScenario(index):
    printFunctionName()
    print("index: {}".format(index))

    scenarios = [testScenario_0, testScenario_1, testScenario_2]
    bs = scenarios[index]() if index < len(scenarios) else []

    print([[hex(x) for x in b.serialize()] for b in bs])

    for i in range(10):
        if i < len(bs): 
            replaceBehaviour(i, bs[i])
        else:
            deleteBehaviour(i)
        pygame.time.delay(200)

# ================================= Main loop =================================
class Main:
    #construction
    def __init__(self):
        # Create new instance of Bluenet
        print(inspect.getfile(ControlType))
        for v in ControlType:
            print(v)

        self.bluenet = Bluenet()

        self.initialized = False

        while not self.initialized:
            inpt = input("input ACM port number: ")

            n = None
            try:
                n = int(inpt)
            except:
                print("couldn't cast input to integer, aborting")
                break

            try:
                self.bluenet.initializeUSB("/dev/ttyACM{0}".format(n))
                self.initialized = True
                break
            except:
                print("coudn't find /dev/ttyACM{0}, try next port".format(n))


        # for i in range(4):
        #     try:
        #         self.bluenet.initializeUSB("/dev/ttyACM{0}".format(i))
        #         self.initialized = True
        #         break
        #     except:
        #         print("coudn't find /dev/ttyACM{0}, trying next port".format(i))

        if not self.initialized:
            print("Failed to connect.")
            return

        pygame.init()
        self.window = pygame.display.set_mode((400,400))
    
    # implements 'with' interface to enforce timely destruction even when Bluenet wants
    # to stay alive.
    def __enter__(self):
        # Set up event listeners
        self.subscriptionId = BluenetEventBus.subscribe(SystemTopics.uartNewPackage, WhatToDoWithUartData)
        self.subscriptionId = BluenetEventBus.subscribe(UsbTopics.newDataAvailable, WhatToDoWithUartData)
        return self
    
    def __exit__(self, type, value, traceback):
        print("goodbye cruel world")
        pygame.quit()
        BluenetEventBus.unsubscribe(self.subscriptionId)
        self.bluenet.stop()

  

    #actual work for this example
    def run(self):
        if not self.initialized:
            print("Not going to run if not initialized.")
            return

        print("saveBehaviour Example up and running")

        run = True
        is_on = True #toggle state for switch call
        behaviourHandler_isActive = True
        dim_toggle = True # toggle allow dimming state
        lock_toggle = True # toggle locked state
        current_room = 0 # use r+[0-9] to change current room, and p+[0-9] to notify user presence in current room. 

        while run:
            pygame.time.delay(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord(' '):
                        # ----- send generic test event over internal evt bus -----
                        propagateEventToCrownstone(0xffff,[])
                    elif event.key == ord('i'):
                        # ----- get indicices -----
                        getBehaviourIndices()
                    elif event.key in [ord(x) for x in "0123456789"]:
                        # ----- edit behaviours -----
                        index = event.key - ord('0')
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            # ----- delete -----
                            deleteBehaviour(index)
                        elif pygame.key.get_mods() & pygame.KMOD_ALT:
                            # ----- replace -----
                            replaceBehaviour(index,SwitchBehaviour.example())
                        elif pygame.key.get_pressed()[pygame.K_t]:
                            # ----- set time -----
                            setTime(index)
                        elif pygame.key.get_pressed()[pygame.K_u]:
                            # ----- suntime -----
                            setSunTime(index)
                        elif pygame.key.get_pressed()[pygame.K_r]:
                            print("set current room to {}".format(index))
                            current_room = index
                        elif pygame.key.get_pressed()[pygame.K_p]:
                            # ----- mock event on crownstone event bus -----
                            sendPresence(current_room,index)
                        elif pygame.key.get_pressed()[pygame.K_RETURN]:
                            SetupBehaviourTestScenario(index)
                        elif pygame.key.get_pressed()[pygame.K_s]:
                            # ----- switch -----
                            switch(11*index) # [0,9] -> [0,99]
                        elif pygame.key.get_pressed()[pygame.K_w]:
                            # ----- switch -----
                            setTwilight(11*index) # [0,9] -> [0,99]
                        elif pygame.key.get_pressed()[pygame.K_e]:
                            # ----- extension -----
                            setExtendedBehaviour(11*index) # [0,9] -> [0,99]
                        else:
                            # ----- get -----
                            getBehaviour(index)
                    elif event.key == pygame.K_t and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        # set time to current
                        setTimeSecSinceMidnight(currentTimeSecSinceMidnight())
                    elif event.key == pygame.K_b:
                        # ----- behaviour handler active -----
                        behaviourHandler_isActive = not behaviourHandler_isActive
                        setBehaviourHandlerActive(behaviourHandler_isActive)
                    elif event.key == pygame.K_c:
                        # ----- clear the presence buffer on the crownstone
                        sendPresence(0xff,0xff)
                    elif event.key == pygame.K_d:
                        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            gotoDfu()
                        else:
                            # ----- dim -----
                            setAllowDimming(dim_toggle)
                            dim_toggle ^= True
                    elif event.key == pygame.K_l:
                        # ----- lock -----
                        setLocked(lock_toggle)
                        lock_toggle ^= True
                    elif event.key == pygame.K_q:
                        run = False

if __name__ == "__main__":
    with Main() as m:
        m.run()