"""Module for reading the image metadata."""
import os
import yaml


class Image:
    """read/create some image related metadata."""

    METADATA_EXT = '.metadata'

    def __init__(self, image_path):
        """Initialize all attributes with default values."""
        self.image_path = image_path
        self.basename = os.path.basename(self.image_path)
        self.dirname = os.path.dirname(image_path)
        self.image_root = self.basename.split('.')[0]
        self.metadata_filename = self.image_root + self.METADATA_EXT
        self.metadata_path = os.path.join(self.dirname, self.metadata_filename)

    @property
    def has_metadata(self):
        return os.path.isfile(self.metadata_path)

    @property
    def size_mb(self):
        try:
            size = os.path.getsize(self.image_path)
            size = int(size / 1024 / 1024)
        except OSError:
            size = 0
        return size

    @property
    def metadata(self):
        metadata = {}
        try:
            with open(self.metadata_path, "r") as f:
                parsed_yaml = yaml.load(f)
        except (yaml.scanner.ScannerError, yaml.YAMLError, OSError, IOError):
            parsed_yaml = {}
        finally:
            metadata['image_file'] = self.basename
            metadata['name'] = parsed_yaml.get("name", None)
            metadata['distribution'] = parsed_yaml.get("distribution", None)
            metadata['distribution_version'] = \
                parsed_yaml.get("distribution_version", None)
            metadata['architecture'] = parsed_yaml.get("architecture", None)
            metadata['active'] = parsed_yaml.get("active", True)
            metadata['internal'] = parsed_yaml.get("internal", False)
            metadata['minimal'] = parsed_yaml.get("minimal", True)
            try:
                created_at = parsed_yaml.get("created_at", None)
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                created_at = None
            metadata['created_at'] = created_at
            try:
                updated_at = parsed_yaml.get("updated_at", None)
                updated_at = updated_at.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                updated_at = None
            metadata['updated_at'] = updated_at
            metadata['services'] = parsed_yaml.get("services", [])
            metadata['min_disk_gb'] = parsed_yaml.get("min_disk", None)
            metadata['min_ram_mb'] = parsed_yaml.get("min_ram", None)
            metadata['author'] = parsed_yaml.get("author", None)
            metadata['size_mb'] = self.size_mb
        return metadata

    @property
    def signature(self):
        signature_path = self.image_path + ".sig"
        try:
            with open(signature_path, "r") as f:
                signature = f.read()
        except (IOError, OSError, UnicodeDecodeError):
            signature = None
        return signature
