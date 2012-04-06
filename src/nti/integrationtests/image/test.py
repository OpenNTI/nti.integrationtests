'''
Created on Apr 5, 2012

@author: ltesti
'''
import os
import sys
#import Tkinter as tk
#from tkFileDialog import askopenfilename
#from tkMessageBox import showerror, showinfo
from subprocess import check_call, CalledProcessError
from os.path import isfile, splitext

def convert(pdf):
    '''Convert a PDF to JPG'''
    if not os.path.exists(pdf):
        print pdf
        print 'error'
        sys.exit()
#        assert("ERROR", "Can't find %s" % pdf)
        return

    jpg = splitext(pdf)[0] + ".jpg"
    print jpg

    try:
        check_call(["convert", "-quality", "100%", pdf, jpg])
#        showinfo("Converted", "{0} converted".format(pdf))
    except (OSError, CalledProcessError) as e: 
        assert 'error'
#        showerror("ERROR", "ERROR: {0}".format(e))

def main():
    
    jpg = '/Users/ltesti/Documents/pdf2png/pngs/solngeomB_1.pdf'
    convert(jpg)
    
if __name__ == "__main__":
    main()
    
    
#def select_file(entry):
#    '''Select a file into entry'''
#    filename = askopenfilename()
#    if not filename:
#        return
#
#    entry.delete(0, tk.END)
#    entry.insert(0, filename)
#
#
#    root = tk.Tk()
#    root.title("PDF to JPEG converter")
#
#    # PDF File: _________________ [...]
#    frame = tk.Frame(root)
#    tk.Label(frame, text="PDF File:").pack(side=tk.LEFT)
#    pdf = tk.Entry(frame, width=60)
#    pdf.pack(side=tk.LEFT)
#    tk.Button(frame, text="...",
#              command=lambda: select_file(pdf)).pack(side=tk.LEFT)
#    frame.pack()
#
#    # [Convert] [Quit]
#    frame = tk.Frame(root)
#    tk.Button(frame, text="Convert",
#              command=lambda: convert(pdf.get())).pack(side=tk.LEFT)
#    tk.Button(frame, text="Quit", command=root.quit).pack(side=tk.LEFT)
#    frame.pack(side=tk.LEFT)
#
#    root.mainloop()