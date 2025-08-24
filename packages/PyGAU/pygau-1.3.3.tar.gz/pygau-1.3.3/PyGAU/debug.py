import inspect as _inspect

class Report:

    """
    Report/trace/print each function as you call. As simply as adding a decorator to them.
    """

    def __init__(self):
        
        self.function_stack = []

    def report_function_stack(self, report_end: bool = True, enable: bool = True, report_parameters: bool = True):

        """
        Decorator for reporting a full stack of functions, only reporting the decorated ones.

        The parameters and their meaning are:
            - report_end: bool = whatever it should also report when the function stops execution (apart from when it starts), by default true.
            - enable: bool = indicates if the report is done or not in general, by default true.
            - report_parameters: bool = whatever the parameters of the function debugged are also reported.
        """

        def decorator(func):

            if enable:

                def modified_behaviour(*args, **kwargs):

                    caller_frame = _inspect.stack()[1].frame #gets the caller frame
                    #caller_func = caller_frame.f_globals.get(caller_frame.f_code.co_name) #get the caller function
                    caller_code = caller_frame.f_code

                    stack = _inspect.stack()

                    extra_indentation = -1

                    for idx in range(len(stack)):
                        
                        if idx == 0:
                            continue #skip, because is the current function

                        if self.function_stack and stack[idx].frame.f_code == self.function_stack[-1].__code__: #recursive call
                            self.function_stack.append(func)
                            extra_indentation = idx - 1

                    if extra_indentation == -1: #somehow hasn't found the caller, must be external.
                        self.function_stack = []
                        self.function_stack.append(func)

                    indentation_level = len(self.function_stack)

                    for extra in range(extra_indentation):
                        print("│ "*(indentation_level-1 + extra) + f"├ \033[90m[A non-decorated function starts executing]\033[0m")

                    print("│ "*(indentation_level-1  + extra_indentation) + f"├ \033[32mStarted execution of\033[0m \033[33m{func.__name__}\033[0m")
                    if report_parameters:
                        print("│ "* (indentation_level + extra_indentation) + f"├ Parameters: {args}")
                        print("│ "* (indentation_level + extra_indentation) + f"├ Keyword parameters: {kwargs}")

                    bullshit = func(*args, **kwargs)

                    if report_end:

                        print("│ "*(indentation_level-1 + extra_indentation) + f"├ \033[31mEnded execution of\033[0m \033[33m{func.__name__}\033[0m")

                        for extra in range(extra_indentation):
                            print("│ "*(indentation_level-1 + extra) + f"├ \033[90m[A non-decorated function ends execution]\033[0m")

                    self.function_stack.pop()

                    return bullshit

                return modified_behaviour
            
            else:

                return func #do no changes
        
        #decorator._wrapper = self
        return decorator
    
    def report_function(report_end: bool = True, enable: bool = True, report_parameters: bool = True):

        """
        Decorator for reporting when a function starts executing and ends.

        The parameters and their meaning are:
            - report_end: bool = whatever it should also report when the function stops execution (apart from when it starts), by default true.
            - enable: bool = indicates if the report is done or not in general, by default true.
            - report_parameters: bool = whatever the parameters of the function debugged are also reported.
        """

        def decorator(func):

            if enable:

                def modified_behaviour(*args, **kwargs):

                    print(f"Started execution of {func.__name__}")
                    if report_parameters:
                        print(f"    - Parameters: {args}")
                        print(f"    - Keyword parameters: {kwargs}")

                    bullshit = func(*args, **kwargs)

                    if report_end:
                        print("Ended execution of", func.__name__)

                    return bullshit

                return modified_behaviour
            
            else:

                return func #do no changes
        
        return decorator