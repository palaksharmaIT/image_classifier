from django import forms
from .models import UploadedImage

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_SIZE_BYTES = 8 * 1024 * 1024  # 8 MB


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        fields = ["image"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "id": "file-input",
            })
        }

    def clean_image(self):
        uploaded_file = self.cleaned_data["image"]

        if uploaded_file.content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError(
                "Unsupported file type. Please upload a JPEG, PNG, or WEBP image."
            )

        if uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
            raise forms.ValidationError(
                "File too large. Please upload an image under 8 MB."
            )

        return uploaded_file