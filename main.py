import os
import re
import fitz
import csv


def getPDFs(path):
    """
    create a list of Document objects for every pdf in a directory
    """
    pdfs = []
    for root, dirs, files in os.walk(path):
        for file in files: 
            if file.endswith(".pdf"):
                doc = fitz.open(os.path.join(root, file))  
                pdfs.append(doc)       
    
    return pdfs

def writeMergedPDF(docs, path):
    result = fitz.open()

    for doc in docs:
        result.insert_pdf(doc)
    
    result.save(path)

def getText(doc: fitz.Document):
    """
    Get all the text from every page in a Document
    """
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def getName(doc: fitz.Document):
    """
    Looks for the name of
    """
    try:
        text = getText(doc)
        return re.search(r"Patient Name\n*(.*?)\n*\([0-9]+\)", text).group(1).strip()
    except AttributeError:
        return ""

def getMRN(doc: fitz.Document):
    """
    Looks for the MRN of
    """
    try:
        text = getText(doc)
        return re.search(r"Patient Name\n*(.*?)\n*\(([0-9]+)\)\nLegal", text).group(2).strip()

    except AttributeError:
        return ""

def getAddress(doc: fitz.Document):
    try:
        text = getText(doc)
        return re.search(r"Patient Demographics\s*(Address|Address \(Permanent\))((\w|\s)*?)(Phone|E-mail Address|PCP)", text).group(2).strip()
    except AttributeError:
        text = getText(doc)
        print(text)
        return "error"

def saveDocInfoToCSV(docs, path):
     with open(path, "w") as f:
        spamwriter = csv.writer(f)
        spamwriter.writerow(['Name', 'MRN', 'Address'])
        for doc in docs:
            spamwriter.writerow([getName(doc), getMRN(doc), getAddress(doc)])

if __name__ == "__main__":
    startingPath = os.path.dirname(os.path.abspath(__file__))
    print("Getting all pdfs in", os.path.join(startingPath, "pdfs"))
    pdfs = getPDFs(startingPath)
    print("Sorting pdfs...")
    pdfs.sort(key=getName)
    for pdf in pdfs:
        print(getText(pdf))
    saveDocInfoToCSV(pdfs, os.path.join(startingPath, "infos.csv"))
    writeMergedPDF(pdfs, os.path.join(startingPath, "combine_fitkit.pdf"))