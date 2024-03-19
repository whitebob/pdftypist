import sys
import getpass

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams

import io
import os

def convert_pdf_to_txt(pdf_path, password=None):
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()

    # 如果密码为空，则尝试从命令行获取或提示用户输入
    if not password:
        if len(sys.argv) == 3:  # 命令行传入密码
            password = sys.argv[2]
        else:  # 提示用户输入密码
            password = getpass.getpass("请输入PDF文件的密码（若无则直接回车）：")


    device = PDFPageAggregator(rsrcmgr,laparams=laparams)

    with open(pdf_path, 'rb') as fp:
        retstr = io.StringIO()
        #retstr.write("D:OK\n")
        retstr.write("S:\n")
        cnt = 1 
        index = 1
        doc = PDFDocument()
        doc.initialize("")
        parser = PDFParser(fp)

        parser.set_document(doc)
        doc.set_parser(parser)

        interpreter = PDFPageInterpreter(rsrcmgr, device)

        try:
            for page in doc.get_pages():
                interpreter.process_page(page)
                layout = device.get_result()
                for out in layout:
                    if hasattr(out, 'get_text'): 
                        for line in out.get_text().split('\n'):
                            if line != '':
                                if cnt <= int(os.getenv('LINES') or 24) - 3:
                                    retstr.write(" :")
                                else:
                                    cnt = 0
                                    index = index + 1
                                    retstr.write(str.format("B: Page {}\n", index))
                                    #retstr.write("D:")
                                    retstr.write("S:")
                                retstr.write(line)
                                retstr.write("\n")
                                cnt = cnt + 1
                    else:
                        #print(type(out))
                        pass
                
        except Exception as e:
            print(f"错误：无法处理PDF文件，可能原因是密码错误或文件不可读。{e}")
            sys.exit(1)

        retstr.write("X:\n")
        text = retstr.getvalue()

    device.close()
    retstr.close()

    txt_path = f"{os.path.splitext(pdf_path)[0]}.typ"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"PDF转TYP完成，结果保存在：{txt_path}")

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python pdf_to_txt.py <pdf_file_path> [<password>]")
    else:
        pdf_file_path = sys.argv[1]
        if len(sys.argv) == 3:
            password = sys.argv[2]
        else:
            password = None
        convert_pdf_to_txt(pdf_file_path, password)

# 或者仅通过命令行调用时接收密码参数，如果未提供则提示用户输入
# if len(sys.argv) != 2:
#     print("Usage: python pdf_to_txt.py <pdf_file_path>")
# else:
#     pdf_file_path = sys.argv[1]
#     password = None
#     convert_pdf_to_txt(pdf_file_path, password)
