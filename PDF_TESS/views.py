from django.shortcuts import render, redirect
from .models import PDF, ExtractedText
import pytesseract
from .forms import PDFUploadForm
from pdf2image import convert_from_path
import os
from django.conf import settings
import cv2
import numpy as np
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            pdf = PDF(file=pdf_file)
            pdf.save()

            images = convert_from_path(pdf.file.path)
            pytesseract.pytesseract.tesseract_cmd = (r"C:\Program Files\Tesseract-OCR\tesseract.exe")
            
            for i, image in enumerate(images):
                image_filename = f'{pdf.file.name}_page_{i+1}.png'
                image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_filename.replace('/', '_'))


                # Save the image
                image.save(image_path)

                result = preprocess_image(image_path)
                
                prepro_path = os.path.join(settings.MEDIA_ROOT, 'prepro', image_filename.replace('/', '_'))
                
                cv2.imwrite(prepro_path + f'{pdf.file.name}_page_{i+1}.png', result)

                # Save the image path in the database
                text = pytesseract.image_to_string(image, lang='mar')
                extracted_text = ExtractedText(pdf=pdf, page_number=i+1, text=text, image_path=image_path)
                extracted_text.save()

            return redirect('pdf_list')

    else:
        form = PDFUploadForm()
    return render(request, 'upload_pdf.html', {'form': form})

def pdf_list(request):
    pdfs = PDF.objects.all()
    return render(request, 'pdf_list.html', {'pdfs': pdfs})


def preprocess_image(image_path):
    # Read the original image
    original_img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply thresholding
    _, binary = cv2.threshold(blur, 160, 220, cv2.THRESH_BINARY)

    #remove borders
    
    # Noise reduction
    # denoised = noise_removal(binary)

    #Deskew Image
    def deskew(cvImage):
        angle = getSkewAngle(cvImage)
        return rotateImage(cvImage, -1.0 * angle)
    fixed = deskew(binary)
    no_borders = remove_borders(fixed)
    
    return no_borders

def noise_removal(image):
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.dilate(image, kernel, iterations=1)
    image = cv2.GaussianBlur(image, (5,5),0)
    return (image)

def getSkewAngle(cvImage):
    # Prep image, copy, convert to gray scale, blur, and threshold
    newImage = cvImage.copy()

    # Find all contours
    contours, hierarchy = cv2.findContours(newImage, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)
    for c in contours:
        rect = cv2.boundingRect(c)
        x,y,w,h = rect
        cv2.rectangle(newImage,(x,y),(x+w,y+h),(0,255,0),2)

    # Find largest contour and surround in min area box
    largestContour = contours[0]
    print (len(contours))
    minAreaRect = cv2.minAreaRect(largestContour)
    cv2.imwrite("temp/boxes.jpg", newImage)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    print(angle)
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle
# Rotate the image around its center
def rotateImage(cvImage, angle: float):
    newImage = cvImage.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage
# Deskew image

def remove_borders(image):
    contours, heiarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntsSorted = sorted(contours, key=lambda x:cv2.contourArea(x))
    cnt = cntsSorted[-1]
    x, y, w, h = cv2.boundingRect(cnt)
    crop = image[y:y+h, x:x+w]
    return (crop)
#++++++++++++++++++++++++++++++++++++++++++++++++++
