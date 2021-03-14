from file import File


class Yaml(File):
    @staticmethod
    def parse_as_json():
        return {  # TODO: get json based on input yaml
            "test_pipeline": {
                "name": "test pipeline",
                "inputs": ["document_id", "page_num"],
                "outputs": ["extractions"],
                "components": {
                    "image_preprocessing": {
                        "runner": "test_data.ImagePreprocessing",
                        "inputs": ["document_id", "page_num"],
                        "outputs": ["page_id"],
                    },
                    "image_ocr": {
                        "runner": "test_data.OCRModel",
                        "inputs": ["image_preprocessing.page_id"],
                        "outputs": ["page_id"],
                    },
                    "extractor": {
                        "runner": "test_data.ExtractionModel",
                        "inputs": ["image_ocr.page_id"],
                        "outputs": ["extractions"],
                    },
                },
            }
        }
