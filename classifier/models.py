from django.db import models


class UploadedImage(models.Model):
    image = models.ImageField(upload_to="uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Image #{self.id} ({self.uploaded_at:%Y-%m-%d %H:%M:%S})"