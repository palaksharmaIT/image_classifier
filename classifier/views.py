import logging
from io import BytesIO

from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import ImageUploadForm
from .models import UploadedImage
from .ml_service import classify_image, generate_gradcam_overlay

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 8


def index(request):
    error_message = None

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            try:
                instance.predictions = classify_image(instance.image.path, top_k=3)

                # Generate Grad-CAM heatmap and attach it to the instance.
                heatmap_img = generate_gradcam_overlay(instance.image.path)
                buffer = BytesIO()
                heatmap_img.save(buffer, format="JPEG", quality=85)
                instance.heatmap_image.save(
                    f"heatmap_{instance.id}.jpg",
                    ContentFile(buffer.getvalue()),
                    save=False,
                )
                instance.save()
            except Exception:
                logger.exception("Inference failed for %s", instance.image.path)
                instance.delete()
                error_message = "Something went wrong while classifying this image."
                form = ImageUploadForm()
                history = UploadedImage.objects.exclude(predictions__isnull=True)[:HISTORY_LIMIT]
                return render(request, "classifier/index.html", {
                    "form": form, "error_message": error_message, "history": history,
                })
            return redirect(reverse("index") + f"?uploaded={instance.id}")
    else:
        form = ImageUploadForm()

    uploaded_image_url = None
    heatmap_image_url = None
    predictions = None

    uploaded_id = request.GET.get("uploaded")
    if uploaded_id:
        try:
            instance = UploadedImage.objects.get(id=uploaded_id)
            uploaded_image_url = instance.image.url
            predictions = instance.predictions
            if instance.heatmap_image:
                heatmap_image_url = instance.heatmap_image.url
        except UploadedImage.DoesNotExist:
            pass

    history = UploadedImage.objects.exclude(predictions__isnull=True)[:HISTORY_LIMIT]

    context = {
        "form": form,
        "predictions": predictions,
        "uploaded_image_url": uploaded_image_url,
        "heatmap_image_url": heatmap_image_url,
        "error_message": error_message,
        "history": history,
    }
    return render(request, "classifier/index.html", context)