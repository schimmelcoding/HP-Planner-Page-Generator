# import dependecies
import argparse

from PyPDF2 import PdfWriter, PdfReader
import io
import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch,mm

FONT = "Helvetica"

BOX = 5*mm
BOX_WIDTH = 31
BOX_HEIGHT = 42
PLANNER_PAGE = (7*inch, 9.5*inch)


RIGHT_PAGE_OFFSET_X = 46 
RIGHT_PAGE_OFFSET_Y = 39 

LEFT_PAGE_OFFSET_X = 25
LEFT_PAGE_OFFSET_Y = 39
WIDTH = 7*inch

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [start date in mm/dd/yyyy]",
        description = "Generate printable pdf of BUJO week planner",
    )

    parser.add_argument("-i", "--input", default="Weekly Continuing-merged.pdf", dest="infile")
    parser.add_argument("-o", "--output", default="destination.pdf", dest="outfile")
    parser.add_argument("startdate")
    return parser 

def getBoxX(numBoxes, left=True):
    if left:
        return BOX*numBoxes + LEFT_PAGE_OFFSET_X
    return BOX*numBoxes+RIGHT_PAGE_OFFSET_X

def getBoxY(numBoxes, left=True):
    if left:
        return BOX*numBoxes + LEFT_PAGE_OFFSET_Y
    return BOX*numBoxes+RIGHT_PAGE_OFFSET_Y

def printString(can, boxStart, string, left=True):
    for i in range(len(string)):
        can.drawString(getBoxX(boxStart[0]+i, left=left), getBoxY(boxStart[1], left=left), string[i])

def fillRightWeek(tue, wed, sat, sun):
    #set page up
    page = io.BytesIO()
    can = canvas.Canvas(page, pagesize=PLANNER_PAGE)
    can.setFillColorRGB(0,0,0)
    can.setFont(FONT,14)
    tueBoxStart=(1,22)
    wedBoxStart=(16,22)
    satBoxStart=(1,1)
    sunBoxStart=(16,1)

    #populate Tuesday
    printString(can, tueBoxStart, tue, left=False)
    
    #populate Wednesday
    printString(can, wedBoxStart, wed, left=False)

    #pupulate Saturday
    printString(can, satBoxStart, sat, left=False)

    #poplate Sunday
    printString(can, sunBoxStart, sun, left=False)

    can.save()
    page.seek(0)
    return page

def fillLeftWeek(mon, thu, fri):
    # set up page
    page = io.BytesIO()
    can = canvas.Canvas(page, pagesize=PLANNER_PAGE)
    can.setFillColorRGB(0,0,0)
    can.setFont(FONT,14)
    monBoxStart=(16,23)
    thuBoxStart=(1,2)
    friBoxStart=(16,2)
    
    #populate Monday
    printString(can, monBoxStart, mon)

    #pupulate thursday
    printString(can, thuBoxStart, thu)

    #poplate Friday
    printString(can, friBoxStart, fri)

    can.save()
    page.seek(0)
    return page

def fillDayLeft(dateString, dayOfWeek):
    page = io.BytesIO()
    can = canvas.Canvas(page, pagesize=PLANNER_PAGE)
    can.setFillColorRGB(0,0,0)
    can.setFont(FONT, 14)
    dateBoxStart = (0,BOX_HEIGHT)
    dowBoxStart = (BOX_WIDTH-len(dayOfWeek),BOX_HEIGHT)
    printString(can, dateBoxStart, dateString)
    printString(can, dowBoxStart, dayOfWeek)
    can.save()
    page.seek(0)
    return page

def fillDayRight(dateString, dayOfWeek):
    page = io.BytesIO()
    can = canvas.Canvas(page, pagesize=PLANNER_PAGE)
    can.setFillColorRGB(0,0,0)
    can.setFont(FONT, 14)
    dateBoxStart = (0,BOX_HEIGHT)
    dowBoxStart = (BOX_WIDTH-len(dayOfWeek),BOX_HEIGHT)
    printString(can, dateBoxStart, dateString, left=False)
    printString(can, dowBoxStart, dayOfWeek, left=False)
    can.save()
    page.seek(0)
    return page

def createWeek(startdate, output, existing_pdf):
    tue =  wed = sat = sun = ""

    # get dates for weekly pages
    for i in range(0,7):
        currDate = startdate + datetime.timedelta(days=i)
        match int(currDate.strftime("%u")):
            case 2:
                tue = currDate.strftime("%d")
            
            case 3:
                wed = currDate.strftime("%d")
            
            case 6:
                sat = currDate.strftime("%d")
            
            case 7:
                sun = currDate.strftime("%d")

    page1 = fillRightWeek(tue,wed,sat,sun)
    new_pdf=PdfReader(page1)

    # read your existing PDF
    #existing_pdf = PdfReader(open("Weekly Continuing-merged.pdf","rb"))
    #output = PdfWriter()

    # merge pages and add to output
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # populate week
    pageNum = 1
    for i in range(0,7):
        currDate = startdate + datetime.timedelta(days=i)
        if int(currDate.strftime("%u")) < 6: # if it is a week day
            #print weekday things
            dateString = currDate.strftime("%B %d %Y")
            dayOfWeek = currDate.strftime("%a")
            page_left = None
            page_left = fillDayLeft(dateString.upper(), dayOfWeek.upper())
            new_pdf = None
            new_pdf = PdfReader(page_left)
    
            page = None
            page = existing_pdf.pages[pageNum]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            pageNum = pageNum + 1

            dateString = currDate.strftime("%m/%d/%y")
            dayOfWeek = currDate.strftime("%A")
            page_right = None
            page_right = fillDayRight(dateString, dayOfWeek.upper())
            new_pdf = None
            new_pdf = PdfReader(page_right)

            page = None
            page = existing_pdf.pages[pageNum]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            pageNum = pageNum + 1
        elif int(currDate.strftime("%u")) == 6 :
            dateString = currDate.strftime("%B %d %Y")
            dayOfWeek = currDate.strftime("%a")
            page_left = None
            page_left = fillDayLeft(dateString.upper(), dayOfWeek.upper())
            new_pdf = None
            new_pdf = PdfReader(page_left)

            page = None
            page = existing_pdf.pages[pageNum]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            pageNum = pageNum + 1

        elif int(currDate.strftime("%u")) == 7:
            dateString = currDate.strftime("%B %d %Y")
            dayOfWeek = currDate.strftime("%a")
            page_right = None
            page_right = fillDayRight(dateString.upper(), dayOfWeek.upper())
            new_pdf = None
            new_pdf = PdfReader(page_right)

            page = None
            page = existing_pdf.pages[pageNum]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            pageNum = pageNum + 1


    #get monday thursday and friday of next week
    mon = thu = fri = ""
    nextweek = startdate + datetime.timedelta(days=7)
    for i in range(0,7):
        currDate = nextweek + datetime.timedelta(days=i)
        match int(currDate.strftime("%u")):
            case 1:
                mon = currDate.strftime("%d")
            case 4:
                thu = currDate.strftime("%d")
            case 5:
                fri = currDate.strftime("%d")

    page14 = fillLeftWeek(mon,thu,fri)
    new_pdf=PdfReader(page14)

    # Then we add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[pageNum]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

def getDateFromStr(datestr):
    date_array = datestr.split("/")
    if not len(date_array) == 3:
        print("exit with error")
    mm = int(date_array[0])
    dd = int(date_array[1])
    yyyy = int(date_array[2])
    
    date = datetime.datetime(yyyy,mm,dd)
    return date

def main():
    parser = init_argparse()
    args = parser.parse_args()
    
    # process startdate into a date
    startDate = getDateFromStr(args.startdate)

    existing_pdf = PdfReader(open(args.infile,"rb"))
    output = PdfWriter()

    createWeek(startDate, output, existing_pdf)

    # And finally, write "output" to a real file:
    outputStream = open(args.outfile,"wb")
    output.write(outputStream)
    outputStream.close()

if __name__ == "__main__":
    main()
