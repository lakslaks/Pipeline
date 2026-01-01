import builtins, re, asyncio 
from .arg_resolver import resolve_args, resolve_func

class PipelineLite:
    
    def __init__(self, steps, pre_compiled=False, custom_objs=None):
        self.steps = steps
        self._result = []
        self.values = {}
        if not pre_compiled:
            self.steps = self.compile_lite(steps, custom_objs)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  

    def execute(self, steps=None):
        steps = steps or self.steps        
        for step in steps:
            try:
                func = step["func"]
                args, kwargs = step.get("args", []), step.get("kwargs", {})
                if asyncio.iscoroutinefunction(func):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(func(*args, **kwargs))
                else:
                    result = func(*args, **kwargs)
                self._result.append(result)
                if (key := step.get('as') or step.get('publish')):
                    self.values[key] = result                
            except Exception as e:
                self._result.append(e.__cause__ or e)
                raise

    def compile_lite(self, full_steps, objs = None):
        registry = {"re": re, "builtins": builtins}
        if objs is not None:
            if isinstance(objs, dict):
                registry.update (objs)
            elif isinstance(objs, (tuple, list)):
                for obj in objs:
                    key = obj.__name__ if inspect.ismodule(obj) else obj.__class__.__name__
                    registry[key] = obj
        compiled = []
        for step in full_steps:
            func = resolve_func(step["action"], registry)
            args, kwargs = resolve_args(step, {})  # Contextless resolution
            compiled.append({"func": func, "args": args, "kwargs": kwargs})
        return compiled

    @property
    def result(self):
        return self._result

    @property
    def last(self):
        return self.result[-1] if self.result else None

if __name__ == '__main__':

    templ = [{'action': 'sub', 'args' : (r'\d', r'', 'text1')}]

    with PipelineLite (templ, False, object_registry) as lite:
        lite.execute ()
        print (lite.result)
