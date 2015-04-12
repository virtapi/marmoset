from contextlib import contextmanager, closing
import libvirt


URI = 'qemu:///system'


@contextmanager
def connection():
    with closing(libvirt.open(URI)) as conn:
        yield conn


class Virt:

    def connection():
        if not 'connection' in vars(self) or self.connection is None:
            self.connection = connection()


    def __del__(self):
        if 'connection' in vars(self) and not self.connection is None:
            self.connection.close()

