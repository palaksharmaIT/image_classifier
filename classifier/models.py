from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to="uploads/")
    heatmap_image = models.ImageField(upload_to="heatmaps/", null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    predictions = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Image #{self.id} ({self.uploaded_at:%Y-%m-%d %H:%M:%S})"

    @property
    def top_prediction(self):
        if self.predictions:
            return self.predictions[0]
        return None

    @property
    def description(self):
        """Builds a natural-language description from the top-3 predictions."""
        if not self.predictions:
            return None

        top = self.predictions[0]
        others = self.predictions[1:]

        text = f"This image is most likely a {top['label']}, with {top['confidence']}% confidence."

        if others:
            other_labels = [f"{p['label']} ({p['confidence']}%)" for p in others]
            text += f" Other possibilities include {', '.join(other_labels)}."

        return text