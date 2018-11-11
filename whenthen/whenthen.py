def whenthen(f):
    class Wrapper:
        def __init__(self, f):
            self._func = f
            self._when_funcs = []
            self._then_funcs = []

        def __call__(self, *args, **kwargs):
            for index, func in enumerate(self._when_funcs):
                if func(*args, **kwargs):
                    return self._then_funcs[index](*args, **kwargs)
            return self._func(*args, **kwargs)

        def when(self, f):
            if len(self._when_funcs) != len(self._then_funcs):
                raise SyntaxError("When must be before then")
            self._when_funcs.append(f)
            return self

        def then(self, f):
            if len(self._when_funcs) - 1 != len(self._then_funcs):
                raise SyntaxError("Then must be after when")
            self._then_funcs.append(f)
            return self

    return Wrapper(f)