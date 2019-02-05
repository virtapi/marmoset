"""Initial file for the image catalog."""

from .catalog import ImageCatalog


def list_all(args):
    """List all images."""
    # pylint: disable-msg=unused-argument
    catalog = ImageCatalog()
    metadata_list = catalog.list_all_metadata()
    for image_metadata in metadata_list:
        print_metadata(image_metadata)


def print_metadata(metadata_dict):
    """Print the image's metadata dict."""
    spacer = '-' * 40
    print('%s\nimage_file: %s\n%s' % (
        spacer, metadata_dict['image_file'], spacer))
    for key, value in sorted(metadata_dict.items()):
        if key != 'image_file':
            print('%s: %s' % (key, value))
