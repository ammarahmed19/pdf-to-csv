import sys
import os
import os.path

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

import re


def convert_pdf(path, format='text', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text


def check_usage():
    if len(sys.argv) != 3:
        print(f'Usage : {sys.argv[0]} input output')
        print('input is the folder that contains the pdfs you want to convert')
        print('output is the folder that the output will be extracted to')
        raise Exception('Please restart the program with the correct arguments')


def get_pdf_names(fname):
    try:
        pdfnames = list(filter(lambda x: x.endswith('.pdf'), os.listdir(fname)))
        dirloc = fname
    except FileNotFoundError:
        pdfnames = list(filter(lambda x: x.endswith('.pdf'), os.listdir(os.path.join(os.getcwd(), fname))))
        dirloc = os.path.join(os.getcwd(), fname)
    except FileNotFoundError:
        raise FileNotFoundError(f'Directory {fname} could not be found')

    return pdfnames, dirloc


def create_dir(oname):
    if not os.path.exists(oname):
        os.makedirs(oname)


def extract_element(text, regex):
    p = re.compile(regex)

    return p.findall(text)


if __name__ == '__main__':

    check_usage()

    fname = sys.argv[1]
    oname = sys.argv[1]

    pdfnames, dirloc = get_pdf_names(fname)

    create_dir(oname)

    for pdfname in pdfnames:
        pdfloc = os.path.join(dirloc, pdfname)
        pdfText = convert_pdf(pdfloc, format='text')

        bates = extract_element(pdfText, ".*-.*-(\d{6,7})")
        dates = extract_element(pdfText, "\d{2}\/\d{2}\/\d{2,4}[\n\s]\d{2}\/\d{2}\/\d{2,4}")
        stock = extract_element(pdfText, "(?:SOLD|BOUGHT)[\n\s]+(.+)")
        acc_num = extract_element(pdfText, "[[:digit:]][[:alpha:]][[:alpha:]]-\d+")
        to_addresses = extract_element(pdfText, "(?<!Office Serving Your Account\n)(?<!\d)([0-9]{1,3} .+\n.+ [A-Z]{2} [0-9]{5}[-]*[0-9]{0,4})")
        from_addresses = extract_element(pdfText, "Merrill Lynch\nOffice Serving Your Account\n([0-9]{1,3} .+\n.+ [A-Z]{2} [0-9]{5}[-]*[0-9]{0,4})")
        price = extract_element(pdfText, "Price[\n\s]+(?=.)([+-]?([0-9]*)(\.([0-9]+))?)")
        quantity = extract_element(pdfText, "")
        trade_date = extract_element(pdfText, "")
        settle_date = extract_element(pdfText, "")
        cusip = extract_element(pdfText, "")
        fa = extract_element(pdfText, "")
        security = extract_element(pdfText, "")
        ml = extract_element(pdfText, "")
