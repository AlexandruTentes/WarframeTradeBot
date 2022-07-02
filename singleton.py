class Singleton(type):
    obj_instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.obj_instances:
            cls.obj_instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls.obj_instances[cls]
