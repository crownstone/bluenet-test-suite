from enum import IntEnum


class EventTypeCategory(IntEnum):
    StateBase                     = 0x000
    InternalBase                  = 0x100
    InternalBaseBluetooth         = InternalBase + 0
    InternalBaseSwitch            = InternalBase + 20
    InternalBasePower             = InternalBase + 40
    InternalBaseErrors            = InternalBase + 60
    InternalBaseStorage           = InternalBase + 80
    InternalBaseLogging           = InternalBase + 100
    InternalBaseADC               = InternalBase + 120
    InternalBaseMesh              = InternalBase + 140
    InternalBaseBehaviour         = InternalBase + 170
    InternalBaseLocalisation      = InternalBase + 190
    InternalBaseSystem            = InternalBase + 210
    InternalBaseTests             = 0xF000,

# corresponds with CS_TYPE
class EventType(IntEnum):
    STATE_BEHAVIOUR_SETTINGS      = 150,

    CMD_SWITCH_OFF                = EventTypeCategory.InternalBaseSwitch + 0
    CMD_SWITCH_ON                 = EventTypeCategory.InternalBaseSwitch + 1
    CMD_SWITCH_TOGGLE             = EventTypeCategory.InternalBaseSwitch + 2
    CMD_SWITCH                    = EventTypeCategory.InternalBaseSwitch + 3
    CMD_SET_RELAY                 = EventTypeCategory.InternalBaseSwitch + 4
    CMD_SET_DIMMER                = EventTypeCategory.InternalBaseSwitch + 5
    CMD_MULTI_SWITCH              = EventTypeCategory.InternalBaseSwitch + 6
    CMD_SWITCHING_ALLOWED         = EventTypeCategory.InternalBaseSwitch + 7
    CMD_DIMMING_ALLOWED           = EventTypeCategory.InternalBaseSwitch + 8
    CMD_SWITCH_AGGREGATOR_RESET   = EventTypeCategory.InternalBaseSwitch + 9

    CMD_SET_TIME                  = EventTypeCategory.InternalBaseSystem + 2

    CMD_UPLOAD_FILTER = EventTypeCategory.InternalBaseLocalisation + 9
    CMD_REMOVE_FILTER = EventTypeCategory.InternalBaseLocalisation + 10
    CMD_COMMIT_FILTER_CHANGES = EventTypeCategory.InternalBaseLocalisation + 11
    CMD_GET_FILTER_SUMMARIES = EventTypeCategory.InternalBaseLocalisation + 12

    CMD_TEST_SET_TIME             = EventTypeCategory.InternalBaseTests + 0


