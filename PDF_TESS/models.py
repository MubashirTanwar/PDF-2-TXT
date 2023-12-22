from django.db import models

class PDF(models.Model):
    file = models.FileField(upload_to='pdfs/')

class ExtractedText(models.Model):
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    text = models.TextField()
    image_path = models.ImageField(upload_to='images/', null=True, blank=True)
