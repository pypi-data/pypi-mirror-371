import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from PIL import Image

from optimizer_middleware.middleware import ImageOptimizationMiddleware


def create_test_image():
    image = Image.new("RGB", (1000, 1000), "red")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    return SimpleUploadedFile("test.jpg", buffer.read(), content_type="image/jpeg")

def test_image_optimization():
    rf = RequestFactory()
    img = create_test_image()
    request = rf.post("/", {"file": img}, format="multipart")

    middleware = ImageOptimizationMiddleware(lambda r: r)
    request = middleware(request)  # returns request because get_response=r

    optimized_file = request.FILES["file"]
    assert optimized_file.name.endswith(".webp")
    assert optimized_file.content_type == "image/webp"

