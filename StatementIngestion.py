import sys
import PyPDF2 as pdf
import re
import csv

def divideByLines(pdfText):
    lines = []
    currLine = ""
    for c in pdfText:
        if c != '\n':
            currLine = currLine + c
        else:
            lines.append(currLine)
            currLine = ""
    
    return lines

def bbva(filename):
    f = open(filename,  "rb")
    csvfile = open("bbva.csv", "w")
    writer = csv.writer(csvfile)
    statement = pdf.PdfFileReader(f)
    n = statement.numPages

    for i in range(n):
        currPage = statement.getPage(i).extractText()

        while True:
            match = re.search("([0-9]{2}/[0-9]{2}/[0-9]{2}[0-9]{2}/[0-9]{2}/[0-9]{2} [A-Z 0-9-]+(([A-Z]{3} |[A-Z]{4})[0-9]{6}[A-Z0-9]{3}){0,1}\*{0,6}[0-9]{0,4}\$[0-9\,]+\.[0-9]{2}-*)", currPage)
            if not match:
                break
            row = []
            movement = currPage[match.span(0)[0] : match.span(0)[1]]

            row.append(movement[0 : 8])

            rfcMatch = re.search("([A-Z]{3} |[A-Z]{4})[0-9]{6}[A-Z0-9]{3}", movement)

            if not rfcMatch:
                if movement.find('*') > 0:
                    row.append(movement[17 : movement.find('*')])
                else:
                    row.append(movement[17 : movement.find('$')])
            else:
                rfcStart = re.search("([A-Z]{3} |[A-Z]{4})[0-9]{6}[A-Z0-9]{3}", movement).span(0)[0]
                row.append(movement[17 : rfcStart])

            row.append(movement[movement.find('$') + 1 :])

            writer.writerow(row)

            currPage = currPage[match.span(0)[1] :]
    return

def hsbc(filename):
    f = open(filename,  "rb")
    csvfile = open("hsbc.csv", "w")
    writer = csv.writer(csvfile)
    statement = pdf.PdfFileReader(f)
    n = statement.numPages

    for i in range(n):
        currPage = statement.getPage(i)
        lines = divideByLines(currPage.extractText())

        for line in lines:
            match = re.search("[0-9]+ [A-Z]{3}([A-Z]{3,4} *[0-9]{6}[A-Z0-9]{3}).*", line)

            if match:
                movement = line[match.span(0)[0] : match.span(0)[1]]
                row = []

                row.append(movement[0 : 6])
                price = re.search("[0-9]+\.[0-9]{2}", movement)
                row.append(movement[19 : price.span(0)[0] - 4])
                row.append(movement[price.span(0)[0] : price.span(0)[1]])
                writer.writerow(row)

    return


if(sys.argv[1] == "hsbc"):
    hsbc(sys.argv[2])
elif(sys.argv[1] == "bbva"):
    bbva(sys.argv[2])