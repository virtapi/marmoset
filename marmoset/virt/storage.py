from . import connection, with_unit, parse_unit, Parent


class Storage(Parent):
    _func = dict(
        all     = 'listAllStoragePools',
        uuid    = 'storagePoolLookupByUUIDString',
        name    = 'storagePoolLookupByName',
        path    = 'storagePoolLookupByPath'
    )

    @property
    def uuid(self):
        return self._resource.UUIDString()

    @property
    def name(self):
        return self._resource.name()

    @property
    def volumes(self):
        vols = self._resource.listAllVolumes()
        return [Volume(v) for v in vols]

    def create_volume(self, name, capacity, allocation=None):
        if not allocation:
            allocation = capacity
        capacity, cunit = parse_unit(capacity)
        allocation, aunit = parse_unit(allocation)
        with open(Volume.template_file()) as f:
            xml = Template(f.read()).substitute(locals())
        with connection() as conn:
            return Volume(self._resouce.createXML(xml))


class Volume(Parent):
    _func = dict(
        key     = 'storageVolLookupByKey',
        path    = 'storageVolLookupByPath'
    )

    Types = {
        0: 'file',
        1: 'block',
        2: 'dir',
        3: 'network',
        4: 'netdir'
    }


    def __init__(self, pool, volume):
        self._pool      = pool
        self._resource  = volume

    def info(self):
        keys = ['type', 'capacity', 'allocation']
        return dict(zip(keys, self._resource.info()))

    @property
    def name(self):
        return self._resource.name()

    @property
    def path(self):
        return self._resource.path()

    @property
    def capacity(self):
        return with_unit(self.info().get('capacity'))

    @property
    def allocation(self):
        return with_unit(self.info().get('allocation'))

    @property
    def type(self):
        return self.__class__.Types[self.info()['type']]
