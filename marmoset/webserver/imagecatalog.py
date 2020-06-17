"""Class for handling image metadata."""
from flask_restful import Resource, abort
from ..imagecatalog.catalog import ImageCatalog


class ImageMetadataCollection(Resource):
    """Collection class to deal with metadata for images."""

    def get(self):
        """List all images' metadata."""
        catalog = ImageCatalog()
        metadata_list = catalog.list_all_metadata()
        return metadata_list


class ImageMetadata(Resource):
    """Class to get metadata for a single image."""

    def get(self, image_file):
        """Get image's metadata."""
        catalog = ImageCatalog()
        image = catalog.get_image(image_file)
        if image is not None:
            return image.metadata
        abort(404)


class ImageSignature(Resource):
    """Class to get signatures for a single image."""

    def get(self, image_file):
        """Return the signature as JSON, if available."""
        catalog = ImageCatalog()
        image = catalog.get_image(image_file)
        if image is not None:
            return {"signature": image.signature}
        abort(404)
