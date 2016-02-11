# Marmoset

Monkeying around with virtual machines and pxe configs.



## Setup

Create `marmoset.conf` before using marmoset! See `Configuration` for details.


### Requirements

* python 3.3+
* libvirt-python3 (or similar package that provides libvirt python bindings)
* Flask
* Flask-RESTful


### Configuration

The configuration file has to be placed in the app's root directory
as `marmoset.conf`. It is necessary to define a `PXELabel` section.
The first entry in this section will be the default label.

All other sections are optional and have defaults set.
An example file can be found as `marmoset.conf.example`.

If you want to customize the XML templates for libvirt objects, copy
the template dir `marmoset/virt/templates/` and specify the new path
in the `Libvirt` section.


## Usage

Marmoset can be used via CLI directly or as a HTTP server.


### CLI

To see all available subcommands and their aliases, just run the script
with the command:

    $ ./marmoset.py -h

Each subcommand provides its own help text:

    $ ./marmoset.py pxe -h


#### PXE

##### Create entries

Create an PXE entry with the default label:

    $ ./marmoset.py pxe create 3.4.5.6

Create an PXE entry for a non-default label:

    $ ./marmoset.py pxe create -l freebsd 3.4.5.6

If the used label has a callback method set that sets a custom root
password for the PXE boot target, you can provide a pasword:

    $ ./marmoset.py pxe c -l freebsd -p SoSecretPW 3.4.5.6


##### List entries

List all entries:

    $ ./marmoset.py pxe list


##### Remove entries

Remove the entry for an IP address:

    $ ./marmoset.py pxe remove 3.4.5.6


#### VM

##### List VMs

List all defined libvirt domains and their attributes:

    $ ./marmoset.py vm list


### HTTP server

Start it like this:

    $ ./marmoset.py server

Or with gunicorn:

    $ gunicorn marmoset.app:app


#### Routes

##### PXE

List all currently set entries:

    curl -u admin:secret http://localhost:5000/v1/pxe

200 on success (empty array if no records are present)
```json
[
  {
    "ip_address": "1.2.3.4",
    "label": "rescue"
  }
]
```

Create a new PXE config entry. Label defaults to "rescue". If nopassword is given, a random password is generated and returned. Takes JSON Input as well:

    curl -u admin:secret --data 'ip_address=10.10.1.1&label=rescue&password=SeCrEt' http://localhost:5000/v1/pxe

201 on success
```json
{
  "ip_address": "10.10.1.1",
  "label": "rescue",
  "password": "SeCrEt"
}
```

409 if there is already an entry

Check if there is an entry currently set:

    curl -u admin:secret http://localhost:5000/v1/pxe/10.10.1.1

200 if found
```json
{
  "ip_address": "10.10.1.1",
  "label": "rescue"
}
```

404 if not found

Destroy an entry:

    curl -u admin:secret -X DELETE http://localhost:5000/v1/pxe/10.10.1.1

204 on success


##### VM

Create a new VM:

    curl -u admin:secret -d 'name=testvm&user=testuser&ip_address=10.10.1.1&memory=1G&disk=10G' http://localhost:5000/v1/vm

201 on success
```json
{
  "disks": [
    {
      "bus": "virtio",
      "capacity": "10 GiB",
      "device": "disk",
      "path": "/mnt/data/test-pool/testuser_testvm",
      "target": "hda",
      "type": "block"
    }
  ],
  "interfaces": [
    {
      "ip_address": "10.10.1.1",
      "mac_address": "52:54:00:47:b0:09",
      "model": "virtio",
      "network": "default",
      "type": "network"
    }
  ],
  "memory": "1 GiB",
  "name": "test",
  "state": {
    "reason": "unknown",
    "state": "shutoff"
  },
  "user": "testuser",
  "uuid": "cd412122-ec04-46d7-ba12-a7757aa5af11",
  "vcpu": "1",
  "vnc_data": {
    "vnc_port": 5900,
    "ws_port": 5700,
    "password": "gferhhpehrehjrekhtngfmbfdkbkre"
  }
}
```

422 if there is an error
 ```json
{
  "message": "useful error message"
}
```

List all currently defined VMs:

    curl -u admin:secret http://localhost:5000/v1/vm
```json
[
  {
    "disks": [
      {
        "bus": "virtio",
        "capacity": "10 GiB",
        "device": "disk",
        "path": "/mnt/data/test-pool/testo",
        "target": "hda",
        "type": "block"
      }
    ],
    "interfaces": [
      {
        "ip_address": "10.10.1.1",
        "mac_address": "52:54:00:47:b0:09",
        "model": "virtio",
        "network": "default",
        "type": "network"
      }
    ],
    "memory": "1 GiB",
    "name": "test",
    "state": {
      "reason": "unknown",
      "state": "shutoff"
    },
    "user": "testuser",
    "uuid": "cd412122-ec04-46d7-ba12-a7757aa5af11",
    "vcpu": "1",
    "vnc_data": {
      "vnc_port": 5900,
      "ws_port": 5700,
      "password": "gferhhpehrehjrekhtngfmbfdkbkre"
    }
  }
]
```

Get info for a specific VM:

    curl -u admin:secret http://localhost:5000/v1/vm/cd412122-ec04-46d7-ba12-a7757aa5af11
200 on success
```json
{
  "disks": [
    {
      "bus": "virtio",
      "capacity": "10 GiB",
      "device": "disk",
      "path": "/mnt/data/test-pool/testuser_testvm",
      "target": "hda",
      "type": "block"
    }
  ],
  "interfaces": [
    {
      "ip_address": "10.10.1.1",
      "mac_address": "52:54:00:47:b0:09",
      "model": "virtio",
      "network": "default",
      "type": "network"
    }
  ],
  "memory": "1 GiB",
  "name": "test",
  "state": {
    "reason": "unknown",
    "state": "shutoff"
  },
  "user": "testuser",
  "uuid": "cd412122-ec04-46d7-ba12-a7757aa5af11",
  "vcpu": "1",
  "vnc_data": {
    "vnc_port": 5900,
    "ws_port": 5700,
    "password": "gferhhpehrehjrekhtngfmbfdkbkre"
  }
}
```

404 if the uuid doesn't exist

Update parameters of a VM:

    curl -u admin:secret -X PUT -d 'memory=3 GiB&cpu=2&password=sEcReT' http://localhost:5000/v1/vm/cd412122-ec04-46d7-ba12-a7757aa5af11

200 on success

```json
{
  "disks": [
    {
      "bus": "virtio",
      "capacity": "10 GiB",
      "device": "disk",
      "path": "/mnt/data/test-pool/testuser_testvm",
      "target": "hda",
      "type": "block"
    }
  ],
  "interfaces": [
    {
      "ip_address": "10.10.1.1",
      "mac_address": "52:54:00:47:b0:09",
      "model": "virtio",
      "network": "default",
      "type": "network"
    }
  ],
  "memory": "3 GiB",
  "name": "test",
  "state": {
    "reason": "unknown",
    "state": "shutoff"
  },
  "user": "testuser",
  "uuid": "cd412122-ec04-46d7-ba12-a7757aa5af11",
  "vcpu": "2",
  "vnc_data": {
    "vnc_port": 5900,
    "ws_port": 5700,
    "password": "sEcReT"
  }
}
```

* 404 if the uuid doesn't exist
* 422 if input values are not processable


Remove a VM:

    curl -u admin:secret -X DELETE http://localhost:5000/v1/vm/cd412122-ec04-46d7-ba12-a7757aa5af11

204 on success


## Setup LDAP + isc-dhcpd
We will do all this in a clean Arch nspawn container (login for a new container is always root without password):
```bash
mkdir marmoset_container
sudo pacman -Syu arch-install-scripts
sudo pacstrap -c -d marmoset_container
sudo systemd-nspawn -b -D marmoset_container/
pacman -Syu git openldap
```

Installing the isc-dhcpd is currently a bit tricky because the default package is not linked against ldap. You can get the sources and replace the PKGBUILD with [mine](https://p.bastelfreak.de/U6f5/) or use the package that I [built](https://p.bastelfreak.de/C6An/). The needed data can be found [here](https://p.bastelfreak.de/t5XS/). Please adjust the params `suffix` and `rootdn` for your needs (in /etc/openldap/slapd.conf), we use `dc=example,dc=com` and `cn=root,dc=example,dc=com` in our example.

```bash
curl -JO https://p.bastelfreak.de/C6An/
pacman -U dhcp*.pkg.tar.xz
cd /etc/openldap/schema
curl -JO https://raw.githubusercontent.com/dcantrell/ldap-for-dhcp/master/dhcp.schema
cd ..
echo 'include /etc/openldap/schema/dhcp.schema' >> slapd.conf
echo 'index dhcpHWAddress eq' >> slapd.conf
echo 'index dhcpClassData eq' >> slapd.conf
cp DB_CONFIG.example /var/lib/openldap/openldap-data/DB_CONFIG
curl https://p.bastelfreak.de/j63 > initial_data.ldif
systemctl start slapd
ldapadd -x -W -D 'cn=root,dc=example,dc=com' -f initial_data.ldif -c
```

Last step, you need to add the following settings to your `/etc/dhcpd.conf` before you start the daemon:
```
ldap-server "localhost";
ldap-port 389;
ldap-username "cn=root, dc=example, dc=com";
ldap-password "secret";
ldap-base-dn "dc=example, dc=com";
ldap-method dynamic;
ldap-debug-file "/var/log/dhcp-ldap-startup.log";
```

```bash
systemctl start dhcpd4.service
```

We also provide a prepacked nspawn container. It has a working openldap + DHCP server,
the openldap is configured to start at boot. Systemd is so awesome that it supports downloading the tar,
so no fiddeling with curl/wget. machinectl will throw the image into a btrfs subvol and requires you to run /var/lib/machines on btrfs:
```bash
pacman -Syu btrfs-progs
modprobe loop
machinectl --verify=no pull-tar https://bastelfreak.de/marmoset_container.tar marmoset_container
machinectl start marmoset_container
machinectl login marmoset_container
```

If you don't run btrfs you can still download the tar to /var/lib/machines, extract it by hand and then continue with the machinectl commands (or start it oldschool like with systemd-nspawn).

## Issues

Find this code at [the git repo](https://www.github.com/virtapi/marmoset/). Find the original code at [the git repo](https://www.aibor.de/cgit/marmoset/).

Contact the original author at code@aibor.de or us in #virtapi at freenode.



## Copyright

GPLv2 license can be found in LICENSE

Copyright (C) 2015 Tobias Böhm code@aibor.de

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

