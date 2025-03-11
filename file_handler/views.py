import pandas as pd
import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import UploadedFile
from django.conf import settings

def upload_file(request):
    """Handles file upload and ensures only the latest file is kept."""
    if request.method == "POST":
        # Delete previous files before saving the new one
        old_files = UploadedFile.objects.all()
        for old_file in old_files:
            file_path = os.path.join(settings.MEDIA_ROOT, str(old_file.file))
            if os.path.exists(file_path):
                os.remove(file_path)
        old_files.delete()  # Clear old database entries

        # Save the new file
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("view_data")

    else:
        form = UploadFileForm()
    return render(request, "file_handler/index.html", {"form": form})

def view_data(request):
    """Displays processed Excel data."""
    latest_file = UploadedFile.objects.last()
    if latest_file:
        file_path = os.path.join(settings.MEDIA_ROOT, str(latest_file.file))
        df = pd.read_excel(file_path)

        if "Brand" in df.columns and "Name" in df.columns:
            df["brand_name"] = df["Brand"].astype(str).str.split(" - ").str[-1] + " " + df["Name"].astype(str)
            df = df[["brand_name"] + [col for col in df.columns if col != "brand_name"]]

        table_html = df.to_html(index=False)
        return render(request, "file_handler/view_data.html", {"table": table_html})

    return render(request, "file_handler/view_data.html", {"table": None})

def download_file(request):
    """Allows users to download the modified Excel file."""
    latest_file = UploadedFile.objects.last()
    if latest_file:
        file_path = os.path.join(settings.MEDIA_ROOT, str(latest_file.file))
        df = pd.read_excel(file_path)

        if "Brand" in df.columns and "Name" in df.columns:
            df["brand_name"] = df["Brand"].astype(str).str.split(" - ").str[-1] + " " + df["Name"].astype(str)
            df = df[["brand_name"] + [col for col in df.columns if col != "brand_name"]]

        output_path = os.path.join(settings.MEDIA_ROOT, "modified_file.xlsx")
        df.to_excel(output_path, index=False)

        with open(output_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/vnd.ms-excel")
            response["Content-Disposition"] = "attachment; filename=modified_file.xlsx"
            return response
    return HttpResponse("No file available.", status=404)
