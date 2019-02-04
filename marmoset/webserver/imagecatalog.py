from flask.ext.restful import Resource, abort
from ..imagecatalog.catalog import ImageCatalog


class ImageMetadataCollection(Resource):

    def get(self):
        """List all images' metadata"""
        catalog = ImageCatalog()
        metadata_list = catalog.list_all_metadata()
        return metadata_list


class ImageMetadata(Resource):
    def get(self, image_file):
        """Get image's metadata"""
        catalog = ImageCatalog()
        image = catalog.get_image(image_file)
        if image is not None:
            return image.metadata
        abort(404)


class ImageSignature(Resource):
    def get(self, image_file):
        catalog = ImageCatalog()
        image = catalog.get_image(image_file)
        if image is not None:
            return {"signature": image.signature}
        abort(404)
