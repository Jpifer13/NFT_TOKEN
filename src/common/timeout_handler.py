import time
from itertools import count
from multiprocessing import Process


class TimeoutDecorator(object):

    func = None

    def __init__(self, exceptions=None, return_value=None, logger=None):
        self._exceptions = exceptions
        self._return_value = return_value
        self._message = None
        self.counter = count(0)

        # Initialize logger
        if logger:
            self._logger = logger

    def __call__(self, *args, **kwargs):
        """
        Call function that runs the wrapped function and catches self._exceptions

        Returns:
            [return_value] -- [Returns whatever the replacement that is defined by the caller or
                None if exception has been caught]
        """
        if self.func is None:
            self.func = args[0]
            return self
        try:
            return self.func(*args, **kwargs)
        except self._exceptions as err:
            # Catch any exception that was given and this is where you can do something
            # to handleor if replacement is given it will return the replacement

            # If a logger was passed it will log excpetion
            if self._logger:
                self._logger.exception(f"Exception caught: {err}")

            # This makes it so you can accept multiple different kinds of return_values
            # so you can customize what response you
            # want to return based on what exception you get
            if self._return_value:
                if type(err) in self._return_value.keys():
                    if hasattr(err, 'message'):  # Checking if self made exception to assign error message
                        self._message = err.message
                    else:
                        self._message = (str(self._return_value[type(err)][1]) + str(err))
                    return {
                        'message':
                        self._message
                    }, int(self._return_value[type(err)][0])
                else:
                    return {'message': str(err)}, 500
            else:
                return {'message': str(err)}, 500
    
    def inc_forever(self):
        print('Starting function inc_forever()...')
        while True:
            time.sleep(1)
            print(next(self.counter))
    
    def return_zero():
        print('Starting function return_zero()...')
        return 0
        