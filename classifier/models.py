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