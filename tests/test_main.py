import os
import shutil
import tempfile
import unittest
from PIL import Image
from compressor.engine import ImageCompressor

class TestImageCompressor(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.engine = ImageCompressor()
        self.sample_img_path = os.path.join(self.test_dir, "sample.png")
        img = Image.new("RGBA", (800, 600), color=(255, 100, 50, 200))
        img.save(self.sample_img_path, format="PNG")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_compress_png_to_jpeg(self):
        out_path = os.path.join(self.test_dir, "output.jpg")
        result = self.engine.compress_single(
            input_path=self.sample_img_path,
            output_path=out_path,
            quality=70,
            target_format="JPEG"
        )
        self.assertTrue(result.success)
        self.assertTrue(os.path.exists(out_path))
        with Image.open(out_path) as res_img:
            self.assertEqual(res_img.format, "JPEG")

    def test_resize_max_dimension(self):
        out_path = os.path.join(self.test_dir, "resized.webp")
        result = self.engine.compress_single(
            input_path=self.sample_img_path,
            output_path=out_path,
            max_dimension=400,
            target_format="WEBP"
        )
        self.assertTrue(result.success)
        with Image.open(out_path) as res_img:
            self.assertLessEqual(max(res_img.size), 400)

    def test_target_kb_binary_search(self):
        out_path = os.path.join(self.test_dir, "target_size.jpg")
        result = self.engine.compress_single(
            input_path=self.sample_img_path,
            output_path=out_path,
            target_format="JPEG",
            target_kb=20
        )
        self.assertTrue(result.success)
        actual_kb = os.path.getsize(out_path) / 1024.0
        self.assertLessEqual(actual_kb, 30.0)

    def test_invalid_file(self):
        bad_path = os.path.join(self.test_dir, "missing.jpg")
        out_path = os.path.join(self.test_dir, "out.jpg")
        result = self.engine.compress_single(bad_path, out_path)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)

if __name__ == "__main__":
    unittest.main()
