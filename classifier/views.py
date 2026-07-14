import logging
from django.shortcuts import render
from .forms import ImageUploadForm
from .ml_service import classify_image

logger = logging.getLogger(__name__)


def index(request):
    predictions = None
    uploaded_image_url = None
    error_message = None

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            uploaded_image_url = instance.image.url

            try:
                predictions = classify_image(instance.image.path, top_k=3)
            except Exception:
                logger.exception("Inference failed for %s", instance.image.path)
                error_message = "Something went wrong while classifying this image."
            form = ImageUploadForm()
    else:
        form = ImageUploadForm()

    context = {
        "form": form,
        "predictions": predictions,
        "uploaded_image_url": uploaded_image_url,
        "error_message": error_message,
    }
    return render(request, "classifier/index.html", context)