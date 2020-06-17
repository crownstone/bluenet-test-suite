
# an event is a method taking no arguments that returns a value which is non-Falsey only when it fails.
# it comes with a time at which it should fire.
# the test will sort the event times and execute them until the first returns a non-Falsey value
# when that happens, it considers the scenario failed and reports back the returned value.
from BluenetTestSuite.testframework.framework import TestFramework

# TODO: actually write an event class with a time and 'onTrigger' field and refactor tests to use them.

from inspect import currentframe

def getLinenumber(frameskip = 0):
    """
    returns the line number of at the call site of this function,
    or the call site of the callers call site, or the call site
    of that callers call site, or etc.. depth depending on frameskip.

    Pass 0 for line no. of callsite of getLineNumber,
    pass 1 for callsite of the current function scope.
    etc.
    """
    cf = currentframe()
    for i in range(frameskip + 1):
        cf = cf.f_back
    return cf.f_lineno

def formatComment(commentstr):
    return "Line {0}: {1}".format(getLinenumber(1), commentstr)

def bind(func, *args):
    """
    Returns a nullary function that calls func with the given arguments.
    """
    def noarg_func():
        return func(*args)
    return noarg_func

def expect(FW, classname, variablename, expectedvalue, errormessage="", verbose=False):
    """
    Checks if the expected value in FW.
    Returns TestFramework failure message when there is one, else None.
    """
    failures = FW.assertFindFailures(classname, variablename, expectedvalue)

    if failures is None:
        failmsg = TestFramework.failure("{2}: no value found for {0}.{1}".format(
            classname, variablename, errormessage))
        if verbose:
            FW.print()

        return failmsg

    actualvalue = FW.getValue(classname,variablename) or "<not found>"

    if failures:
        failmsg = TestFramework.failure("{4}: Expected {0}.{1} to have value {2}, got {3}".format(
            classname, variablename, expectedvalue, actualvalue, errormessage))
        if verbose:
            FW.print()

        return failmsg

    if verbose:
        print("expectation correct: {0}.{1} == {2} ({3})".format(
            classname, variablename, actualvalue, errormessage))
        FW.print()

    return None


def expectAny(FW, classname, variablename, expectedvalues, errormessage="", verbose=False):
    """
    Same as expect, but expected values must be an iterable object containing
    the expectedvalues and will only fail if the classname.variablename doesn't
    match any of the values in this iterable.
    """
    failures = FW.assertFindFailuresMulti(classname, variablename, expectedvalues)
    if failures is None:
        failmsg = TestFramework.failure("{2}: no value found for {0}.{1}".format(
            classname, variablename, errormessage))
        if verbose:
            FW.print()

        return failmsg

    actualvalue = FW.getValue(classname, variablename) or "<not found>"

    if failures:
        failmsg = TestFramework.failure("{4}: Expected {0}.{1} to have value in [{2}], got {3}".format(
            classname, variablename, ",".join(expectedvalues), actualvalue, errormessage))
        if verbose:
            FW.print()

        return failmsg

    if verbose:
        print("expectation correct: {0}.{1} == {2} ({3})".format(
            classname, variablename, actualvalue, errormessage))

    return None
