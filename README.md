# Marmoset

Monkeying around with virtual machines and pxe configs.

---

## Contents
+ [Setup](#setup)
+ [Requirements](#requirements)
+ [Configuration](#configuration)
+ [Usage](#usage)
  - [CLI](#cli)
    - [CLI PXE](#cli-pxe)
    - [CLI VM](#cli-vm)
  - [HTTP Server](#http-server)
    - [HTTP PXE](#http-pxe)
    - [HTTP VM](#http-vm)
    - [HTTP installimage](#http-installimage)
    - [HTTP DHCP](#http-dhcp)
+ [Name origin](#name-origin)
+ [Issues](#issues)
+ [License](#license)
+ [Contact](#contact)
+ [Contribution](#contribution)

---

## Setup

Clone the repo into /opt, then copy the service file into the systemd directory and reload systemd to recognize the file:
```bash
cd /opt
git clone https://github.com/virtapi/marmoset.git
cd marmoset
cp ext/marmoset.service /etc/systemd/system/
systemctl daemon-reload
```
Copy the `marmoset.conf.example` to `marmoset.conf` and adjust the settings to your needs.
Checkout the Comments in the file our our [Configuration](#configuration) section.

Now we need to setup a virtualenv and install the required python packages (remove libvirt from the requirements.txt and `pkg-config libvirt gcc` from the list of packages to install if you don't want to manage VMs with marmoset):
```bash
pacman -Syu python-virtualenv pkg-config libvirt gcc
virtualenv prod
source prod/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Requirements
Please checkout our [requirements.txt](requirements.txt) for a complete and authoritative list!

* aniso8601
* Flask
* Flask-RESTful
* itsdangerous
* Jinja2
* ldap3
* libvirt-python
* MarkupSafe
* pyasn1
* python-dateutil
* pytz
* six
* Werkzeug
* wheel

In addition to these python packages, you also need Python 3. This project originally started with Python 3.3, we are currently developing and testing on 3.5 but we plan to support Python 3.3 and 3.4 as well.
We also need pkg-config and libvirt, which you need to install via your system-wide package manager (these aren't python packages).

---

## Configuration

The configuration file has to be placed in the app's root directory
as `marmoset.conf`. It is necessary to define a `PXELabel` section.
The first entry in this section will be the default label.

All other sections are optional and have defaults set.
An example file can be found as `marmoset.conf.example`.

If you want to customize the XML templates for libvirt objects, copy
the template dir `marmoset/virt/templates/` and specify the new path
in the `Libvirt` section.

---

## Usage

Marmoset can be used via CLI directly or as a HTTP server.


## CLI

To see all available subcommands and their aliases, just run the script
with the command:

    $ ./marmoset.py -h

Each subcommand provides its own help text:

    $ ./marmoset.py pxe -h

### CLI PXE

#### CLI List Entries

List all entries:

    $ ./marmoset.py pxe list

#### Create Entries

Create an PXE entry with the default label:

    $ ./marmoset.py pxe create 3.4.5.6

Create an PXE entry for a non-default label:

    $ ./marmoset.py pxe create -l freebsd 3.4.5.6

If the used label has a callback method set that sets a custom root
password for the PXE boot target, you can provide a pasword:

    $ ./marmoset.py pxe c -l freebsd -p SoSecretPW 3.4.5.6

#### Remove Entries

Remove the entry for an IP address:

    $ ./marmoset.py pxe remove 3.4.5.6

### CLI VM

#### List VMs

List all defined libvirt domains and their attributes:

    $ ./marmoset.py vm list

---

## HTTP Server

Start it like this:

    $ ./marmoset.py server

Or use our systemd service:

    $ systemctl start marmoset

A third solution is to use nginx + uwsgi to power the app. This is the recommended way if you expect a high amount of requests.

### HTTP PXE

#### List Entries

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

#### Create Entries
Create a new PXE config entry. Label defaults to "rescue". If no password is given and a callback method is set, a random password is generated and returned. Takes JSON Input as well:

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

#### Remove Entries

    curl -u admin:secret -X DELETE http://localhost:5000/v1/pxe/10.10.1.1

204 on success


#### HTTP VM

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

### HTTP installimage
This endpoint is meant to work together with our [installimage](https://github.com/virtapi/installimage). We identify each dataset by its MAC address and store the key:value config pairs for the installimage.

#### List Entries
    curl -u admin:secret http://localhost:5000/v1/installimage

```json
[
    {
        "mac": "00_00_00_00_00_00",
        "variables": {
            "BOOTLOADER": "grub",
            "DRIVE1": "/dev/sda",
            "HOSTNAME": "CentOS-71-64-minimal",
            "IMAGE": "/root/.installimage/../images/CentOS-71-64-minimal.tar.gz",
            "PART": "/ ext4 all"
        }
    },
    {
        "mac": "b8_ac_6f_97_7e_77",
        "variables": {
            "BOOTLOADER": "grub",
            "DRIVE1": "/dev/sda",
            "HOSTNAME": "CentOS-71-64-minimal",
            "IMAGE": "/root/.installimage/../images/CentOS-71-64-minimal.tar.gz",
            "PART": "/ ext4 all",
        }
    }
]

```

#### List a single Entry
    curl -u admin:secret http://localhost:5000/v1/installimage/b8:ac:6f:97:7e:77

```json
{
    "mac": "b8:ac:6f:97:7e:77",
    "variables": {
        "BOOTLOADER": "grub",
        "DRIVE1": "/dev/sda",
        "HOSTNAME": "CentOS-71-64-minimal",
        "IMAGE": "/root/.installimage/../images/CentOS-71-64-minimal.tar.gz",
        "PART": "/ ext4 all",
    }
}
```

#### List a single Entry in the installimage format
    curl -u admin:secret http://localhost:5000/v1/installimage/b8:ac:6f:97:7e:77/config

```
PART / ext4 all
IMAGE /root/.installimage/../images/CentOS-71-64-minimal.tar.gz
DRIVE1 /dev/sda
BOOTLOADER grub
HOSTNAME CentOS-71-64-minimal
```

#### Create a record
    curl -u admin:secret --data "drive1=/dev/sda&bootloader=grub&hostname=CentOS-71-64-minimal&PART=/ ext4 all&image=/root/.installimage/../images/CentOS-71-64-minimal.tar.gz" http://localhost:5000/v1/installimage/b8:ac:6f:97:7e:77

Returns the created record:
```json
{
    "mac": "b8:ac:6f:97:7e:77",
    "variables": {
        "BOOTLOADER": "grub",
        "DRIVE1": "/dev/sda",
        "HOSTNAME": "CentOS-71-64-minimal",
        "IMAGE": "/root/.installimage/../images/CentOS-71-64-minimal.tar.gz",
        "PART": "/ ext4 all",
    }
}
```

#### Delete a Record
    curl -u admin:secret -X DELETE http://localhost:5000/v1/installimage/b8:ac:6f:97:7e:77

Errormessage if you want to delete or list a nonexistent entry:
```json
{
    "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again. You have requested this URI [/v1/installimage/b8:ac:6f:97:7e:77] but did you mean /v1/installimage/<mac> or /v1/installimage/<mac>/config or /v1/installimage ?"
}
```

### HTTP DHCP
This endpoint allows us the throw static IP/MAC combinations into a ldap database. Currently tested is only the [openldap](http://www.openldap.org/) backend. This database is connected to an isc-dhcpd. We can identify an object by its IP or MAC address.

#### List Entries
    curl -u admin:secret  http://localhost:5000/v1/dhcp
```json
[
    {
        "additional_statements": {},
        "dhcp_hostname": "odin.fritz.box",
        "gateway": "192.168.10.1",
        "ip_address": "192.168.10.5",
        "mac": "00:00:00:00:00:00",
        "networkmask": "255.255.255.0"
    },
    {
        "additional_statements": {},
        "dhcp_hostname": "odin.fritz.box",
        "gateway": "10.3.7.1",
        "ip_address": "10.3.7.41",
        "mac": "00:00:00:00:00:00",
        "networkmask": "255.255.255.0"
    }
]
```

#### List One Entry based on MAC
    curl -u admin:secret  http://localhost:5000/v1/dhcp/mac/00:00:00:00:00:00
```json
{
  "additional_statements": {},
  "dhcp_hostname": "odin.fritz.box",
  "gateway": "10.3.7.1",
  "ip_address": "10.3.7.41",
  "mac": "00:00:00:00:00:00",
  "networkmask": "255.255.255.0"
}
```

or:
    curl -u admin:secret http://localhost:5000/v1/dhcp/mac/23.45.67.8
```
"please provide a valid mac address"
```

#### List one Entry based on IP
    curl -u admin:secret  http://localhost:5000/v1/dhcp/ipv4/10.3.7.41
```json
{
  "additional_statements": {},
  "dhcp_hostname": "odin.fritz.box",
  "gateway": "10.3.7.1",
  "ip_address": "10.3.7.41",
  "mac": "00:00:00:00:00:00",
  "networkmask": "255.255.255.0"
}
```

or:
  curl -u admin:secret http://localhost:5000/v1/dhcp/ipv4/23.45.67.888
```
"please provide a valid ipv4 address"
```

#### Create a new Entry:
this will return the new created entry:
    curl -u admin:secret --data 'ip_address=10.3.7.41&mac=b8:ac:6f:97:7e:77&gateway=10.3.7.1&networkmask=255.255.255.0' http://localhost:5000/v1/dhcp
```json
{
    "additional_statements": {},
    "dhcp_hostname": "example.com",
    "gateway": "10.3.7.1",
    "ip_address": "10.3.7.41",
    "mac": "b8:ac:6f:97:7e:77",
    "networkmask": "255.255.255.0"
}
```

an update works the same way, just submit the command again and change new updated params, again the API will respond with the updated entry.

#### Delete an Entry:
    curl -u admin:secret -X DELETE http://localhost:5000/v1/dhcp/ipv4/10.3.7.41

Deleting a nonexistent entry:
    curl -u admin:secret -X DELETE http://localhost:5000/v1/dhcp/ipv4/10.3.7.41

will return:
```json
{
  "message": "The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again. You have requested this URI [/v1/dhcp/ipv4/10.3.7.41] but did you mean /v1/dhcp/ipv4/<ipv4> ?"
}
```

---

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

---

## Name Origin
The marmosets is a group of monkey species, checkout [wikipedia](https://en.wikipedia.org/wiki/Marmoset) for detailed infos.

---

## Issues
[Github Issues](https://www.github.com/virtapi/marmoset/issues)

---

## License
The original [project](https://github.com/aibor/marmoset) and all of our changes are based on the AGPL, you can find the license [here](LICENSE).

---

## Contact
You can meet us in #virtapi at freenode.

---

## Contribution
We've defined our contribution rules in [CONTRIBUTING.md](CONTRIBUTING.md).
