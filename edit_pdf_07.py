from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('OpenSans-Light', 'OpenSans-Light.ttf'))
pdfmetrics.registerFont(TTFont('OpenSans-Regular', 'OpenSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('OpenSans-Bold', 'OpenSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))

file_name = 'mypdf.pdf'
file_path = 'C:\\Users\\xx\\Desktop\\pdf_python\\'

packet = io.BytesIO()
# create a new PDF with Reportlab
can = canvas.Canvas(packet, pagesize=letter)
# can.setFont('Times-Roman', 10)
# can.setFont('Arial', 10)
# can.setFont('OpenSans-Regular', 8.2)
# can.setFont('OpenSans-Light', 8.2)

# can.drawString(394, 704, "Hello world")


# can.setFillColorRGB(1,0,0) #choose your font colour
# can.setFillColorRGB(1,1,1) #choose your font colour
# no 1
# can.drawString(395.8, 703.9, "13")
# can.drawString(407.26, 703.9, "Oc")
# can.drawString(417.6, 703.9, "t")

# can.setStrokeColorRGB(1,0,0) #choose your line color
can.setStrokeColorRGB(1,1,1) #choose your line color
can.setLineWidth(9.0)
can.line(396,706,422,706)
# # no 2
# can.drawString(395.8, 703.9, "13")
# can.drawString(407.26, 703.9, "Oc")
# can.drawString(417.6, 703.9, "t")
# can.setStrokeColorRGB(1,0,0) #choose your line color
# can.setStrokeColorRGB(1,1,1) #choose your line color
can.setLineWidth(9.0)
can.line(370,677,396,677)
# # no 3
# can.setStrokeColorRGB(1,0,0) #choose your line color
can.setStrokeColorRGB(1,1,1) #choose your line color
can.setLineWidth(9.0)
can.line(373,662,399,662)

# set new
can.setFont('OpenSans-Regular', 8.0)
# can.setFillColorRGB(1,1,1) #choose your font colour
# can.setFillColorRGB(1,0,0) #choose your font colour
can.setFillColorRGB(0,0,0) #choose your font colour
can.drawString(396, 704.15, "19 Dec")
# no 2
# can.setFillColorRGB(1,0,0) #choose your font colour
can.drawString(370.5, 674.1, "19 Dec")
# # no 3
# can.setFillColorRGB(1,0,0) #choose your font colour
can.drawString(373.5, 659.12, "19 Dec")




can.save()

#move to the beginning of the StringIO buffer
packet.seek(0)
new_pdf = PdfFileReader(packet)
# read your existing PDF
existing_pdf = PdfFileReader(open(file_path + file_name, "rb"))
output = PdfFileWriter()
for n in range(0, 2):
    page = existing_pdf.getPage(n)
    if n == 0:
        page.mergePage(new_pdf.getPage(0))

    output.addPage(page)

# add the "watermark" (which is the new pdf) on the existing page
# page.mergePage(new_pdf.getPage(0))
# output.addPage(page)
# finally, write "output" to a real file
outputStream = open(file_path+"destination.pdf", "wb")
output.write(outputStream)
outputStream.close()