from django.shortcuts import render, redirect
from django.http import HttpResponse
import re
import fitz
from django.core.files.storage import default_storage
import os, shutil
from shutil import make_archive
from wsgiref.util import FileWrapper
# Create your views here.


def login(request):
    return render(request, 'login.html')

def index(request):
    clean_path = 'app/static/pdf'
    clean_folder(clean_path)
    clean_path = 'app/media/pdf_images'
    clean_folder(clean_path)
    return render(request, 'index.html')

def image_index(request):
    clean_path = 'app/static/pdf'
    clean_folder(clean_path)
    clean_path = 'app/media/pdf_images'
    clean_folder(clean_path)
    return render(request, 'photo.html')

def clean_folder(path):
    folder = path
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def generate_pdf_results(file, name_filter, no_of_pages):
    with open('app/static/pdf/data.pdf', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    doc = fitz.open('app/static/pdf/data.pdf')
    results = []
    alltext = ""


    try:
        if int(no_of_pages) > len(doc):
            return None
    except Exception as e:
        print(e)

    length_of_doc = int(no_of_pages)-1 if no_of_pages else len(doc)

    for i in range(length_of_doc):
        page = doc.load_page(i)
        text = page.get_text()
        alltext += text
        page.clean_contents()
        for img in page.get_images():
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:  # this is GRAY or RGB
                try:
                    pix.writePNG("app/media/pdf_images/p%s-%s.png" % (i, xref))
                except Exception as e:
                    print(e)
            else:  # CMYK: convert to RGB first
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                pix1.writePNG("app/media/pdf_images/p%s-%s.png" % (i, xref))
                pix1 = None
            pix = None
            image_name = "p%s-%s.png" % (i, xref)
            results.append({'image_name': "/media/pdf_images/"+image_name})

    dataList = alltext.split('(300)')
    re.DOTALL = True
    count = 0

    for section in dataList:
        try:
            characters = re.findall("[0-9]{6}", section)
            all_section = section.split("\n")


            title = all_section[all_section.index("(732)") + 1]


            #print(all_section)
            before_keyword, keyword, after_keyword = section.partition("(511)")


            number = set([a.split(" ")[0] for a in after_keyword.split("\n") if a.split(" ")[0].isdigit()])

            if name_filter!="" and not any(item in number for item in name_filter.split(" ")):
                count+=1
                continue

            dates = re.findall("../../....", section)

            if len(dates) > 0:
                actual_date = dates[0]

            #print(characters)
            #print(actual_date)
            #print(title)
            #print(number)
            #print("\n")
            results[count]['characters'] = characters[0]
            results[count]['actual_date'] = actual_date
            results[count]['title'] = title
            results[count]['number'] = '; '.join([str(elem) for elem in number])

            count+=1
        except Exception as e:
            print(e)

    if name_filter!="":
        results = [elem for elem in results if 'title' in elem]
    return results


def result(request):
    if(request.method == "POST"):
        clean_path = 'app/static/pdf'
        clean_folder(clean_path)
        clean_path = 'app/media/pdf_images'
        clean_folder(clean_path)

        print(request.POST)

        results = generate_pdf_results(request.FILES['file'], request.POST['name'], request.POST['no_of_pages'])
        context = {
            'results' : results
        }
        return render(request, 'result.html', context)
    else:
        return redirect('index')

def image_extractor(request):
    if(request.method == "POST"):
        clean_path = 'app/static/pdf'
        clean_folder(clean_path)
        clean_path = 'app/media/pdf_images'
        clean_folder(clean_path)

        print(request.POST)

        results = generate_pdf_results(request.FILES['file'], request.POST['name'], request.POST['no_of_pages'])
        context = {
            'results' : results
        }
        return render(request, 'image_extractor.html', context)
    else:
        return redirect('index')

def download_images(request):
    files_path = "app/media/pdf_images"
    path_to_zip = make_archive(files_path, "zip", files_path)
    # print(path_to_zip)
    response = HttpResponse(FileWrapper(open(path_to_zip,'rb')), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="%s"' % 'images.zip'
    return response
