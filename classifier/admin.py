from django.contrib import admin
from django.utils.html import format_html
from .models import UploadedImage


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ("id", "thumbnail", "top_label", "top_confidence", "uploaded_at")
    list_display_links = ("id", "thumbnail")
    readonly_fields = ("uploaded_at", "image_preview", "heatmap_preview", "predictions")
    fields = ("image", "image_preview", "heatmap_image", "heatmap_preview", "predictions", "uploaded_at")
    ordering = ("-uploaded_at",)

    def thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px; width:50px; object-fit:cover; border-radius:6px;" />',
                obj.image.url,
            )
        return "-"
    thumbnail.short_description = "Image"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:300px; border-radius:8px;" />', obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"

    def heatmap_preview(self, obj):
        if obj.heatmap_image:
            return format_html(
                '<img src="{}" style="max-height:300px; border-radius:8px;" />', obj.heatmap_image.url
            )
        return "No heatmap generated"
    heatmap_preview.short_description = "Grad-CAM Preview"

    def top_label(self, obj):
        if obj.top_prediction:
            return obj.top_prediction.get("label", "-")
        return "-"
    top_label.short_description = "Top Prediction"

    def top_confidence(self, obj):
        if obj.top_prediction:
            return f"{obj.top_prediction.get('confidence', 0)}%"
        return "-"
    top_confidence.short_description = "Confidence"