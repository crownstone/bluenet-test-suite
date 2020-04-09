
# an event is a method taking no arguments that returns a value which is non-Falsey only when it fails.
# it comes with a time at which it should fire.
# the test will sort the event times and execute them until the first returns a non-Falsey value
# when that happens, it considers the scenario failed and reports back the returned value.
from testframework.framework import TestFramework

# TODO: actually write an event class with a time and 'onTrigger' field and refactor tests to use them.

def bind(func, *args):
    """
    Returns a nullary function that calls func with the given arguments.
    """
    def noarg_func():
        return func(*args)
    return noarg_func


def expect(FW, classname, variablename, expectedvalue, errormessage=""):
    """
    Checks if the expected value in FW.
    Returns TestFramework failure message when there is one, else None.
    """
    failures = FW.assertFindFailures(classname, variablename, expectedvalue)
    if failures:
        actualvalue = None
        try:
            actualvalue = FW.statedict[failures[0]].get(variablename)
        except:
            actualvalue = "<not found>"

        failmsg = TestFramework.failure("{4}: Expected {0}.{1} to have value {2}, got {3}".format(
            classname, variablename, expectedvalue, actualvalue, errormessage))
        FW.print()
        return failmsg
    else:
        print("expectation correct: {0}.{1} == {2} ({3})".format(
            classname, variablename, expectedvalue, errormessage))

    return None
