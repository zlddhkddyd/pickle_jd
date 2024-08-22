from ImageMetadataProcessor import ImageMetadataProcessor
from ImageCaptionGenerator import ImageCaptionGenerator

class ImageProcessor:
    def __init__(self, openai_api_key):
        self.metadata_processor = ImageMetadataProcessor()
        self.caption_generator = ImageCaptionGenerator(openai_api_key)

    def process_image(self, image_path):
        metadata = self.metadata_processor.process(image_path)
        caption = self.caption_generator.generate_caption(image_path, metadata)
        return {
            'image_path': image_path,
            'metadata': metadata,
            'caption': caption
        }
