from string import Template

from . import base


class Storage(base.Parent):
    DEFAULT = 'default'

    _func = dict(
        all='listAllStoragePools',
        uuid='storagePoolLookupByUUIDString',
        name='storagePoolLookupByName',
        path='storagePoolLookupByPath'
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
        # unfinished impl...
        # pylint: disable-msg=unused-argument
        # pylint: disable-msg=unused-variable
        if not allocation:
            allocation = capacity
        capacity, cunit = base.parse_unit(capacity)
        allocation, aunit = base.parse_unit(allocation)
        with open(Volume.template_file()) as f:
            xml = Template(f.read()).substitute(locals())
        with base.connection() as conn:
            return Volume(self._resource.createXML(xml))


class Volume(base.Parent):
    _func = dict(
        key='storageVolLookupByKey',
        path='storageVolLookupByPath'
    )

    Types = {
        0: 'file',
        1: 'block',
        2: 'dir',
        3: 'network',
        4: 'netdir'
    }

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
        return base.with_unit(self.info().get('capacity'))

    @property
    def allocation(self):
        return base.with_unit(self.info().get('allocation'))

    @property
    def type(self):
        return self.__class__.Types[self.info()['type']]
