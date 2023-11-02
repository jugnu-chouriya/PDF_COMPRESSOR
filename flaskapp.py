from flask import Flask, current_app, render_template, request, send_file, send_from_directory

import argparse
import os.path
import shutil
import subprocess
import sys
x = 0

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "/home/pdqa/flaskapp/uploads"

# Function to convert PDF pages to images and resize
def process_pdf(input_pdf, output_path, output_folder, resize_percentage):
    compress(input_pdf, output_path, power=resize_percentage)


def compress(input_file_path, output_file_path, power=0):
    """Function to compress PDF via Ghostscript command line interface"""
    quality = {
        0: "/default",
        1: "/prepress",
        2: "/printer",
        3: "/ebook",
        4: "/screen"
    }

    # Basic controls
    # Check if valid path
    if not os.path.isfile(input_file_path):
        print("Error: invalid path for input PDF file.", input_file_path)
        sys.exit(1)

    # Check compression level
    if power < 0 or power > len(quality) - 1:
        print("Error: invalid compression level, run pdfc -h for options.", power)
        sys.exit(1)

    # Check if file is a PDF by extension
    if input_file_path.split('.')[-1].lower() != 'pdf':
        print(f"Error: input file is not a PDF.", input_file_path)
        sys.exit(1)

    gs = get_ghostscript_path()
    print("Compress PDF...")
    initial_size = os.path.getsize(input_file_path)
    subprocess.call(
        [
            gs,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality[power]),
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-sOutputFile={}".format(output_file_path),
            input_file_path,
        ]
    )
    final_size = os.path.getsize(output_file_path)
    x= final_size
    ratio = 1 - (final_size / initial_size)
    print("Compression by {0:.0%}.".format(ratio))
    print("Final file size is {0:.5f}MB".format(final_size / 1000000))
    print("Done.")


def get_ghostscript_path():
    gs_names = ["gs", "gswin32", "gswin64"]
    for name in gs_names:
        if shutil.which(name):
            return shutil.which(name)
    raise FileNotFoundError(
        f"No GhostScript executable was found on path ({'/'.join(gs_names)})"
    )

@app.route("/upload", methods=["POST"])
def upload_file():
    if "pdf" in request.files:
        uploaded_file = request.files["pdf"]
        if uploaded_file.filename != "":
            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
            uploaded_file.save(pdf_path)
            return pdf_path

# Route to the main page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf"]
        
        if file:
            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(pdf_path)
            y=os.path.getsize(pdf_path)//1024 # Get resize percentage from the form
            resize_percentage = int(request.form["resize_percentage"])
            val = resize_percentage//25 +1
            if val > 4 : val=4
            # Process the PDF
            pdf_output_path = pdf_path.replace(".pdf", f"_resized_{resize_percentage}.pdf")
            process_pdf(pdf_path, pdf_output_path, app.config["UPLOAD_FOLDER"], val)

            # Create a new PDF from resized images
            x=os.path.getsize(pdf_output_path)//1024
            return render_template("index.html",y=y, pdf_output=pdf_output_path,x=x, pdf_to_view=pdf_output_path)

    return render_template("index.html", pdf_output=None, pdf_to_view=None)

# Route to serve the resized PDF file
@app.route("/download//home/pdqa/flaskapp/uploads/<pdf_filename>")
def download(pdf_filename):
    print("jhbjhbdfj=--=================================================")
    path = '/home/pdqa/flaskapp/uploads/' + pdf_filename
    print(path)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)                                                                                                                                                                       