"""Module for listing all images."""
from .image import Image
import glob
import os


class ImageCatalog:
    IMAGE_DIR = '/srv/nfs/images/'
    IMAGE_EXTENSTIONS = ['tar.gz', 'bin.bz2']

    def __init__(self):
        """We don't initialize anything here."""

    def list_all_image_files(self):
        all_images = []
        if os.path.isdir(self.IMAGE_DIR):
            for extension in self.IMAGE_EXTENSTIONS:
                images = glob.glob1(self.IMAGE_DIR, '*%s' % extension)
                all_images.extend(images)
        return all_images

    def get_image_metadata(self, image_file):
        image = self.get_image(image_file)
        if image is not None:
            return image.metadata
        return None

    def list_all_metadata(self):
        metadata_list = []
        for image in self.list_all_images():
            metadata = image.metadata
            metadata_list.append(metadata)
        return metadata_list

    def get_image_path(self, image_file):
        return os.path.join(self.IMAGE_DIR, image_file)

    def list_all_image_paths(self):
        image_paths = []
        for image_file in self.list_all_image_files():
            image_paths.append(self.get_image_path(image_file))
        return image_paths

    def list_all_images(self):
        images = []
        for image_path in self.list_all_image_paths():
            image = Image(image_path)
            images.append(image)
        return images

    def get_image(self, image_file):
        image_path = self.get_image_path(image_file)
        if os.path.isfile(image_path):
            image = Image(image_path)
        else:
            image = None
        return image
