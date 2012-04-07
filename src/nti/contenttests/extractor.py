import os

from Quartz import kCFURLPOSIXPathStyle
from Quartz import kCGRenderingIntentDefault
from Quartz import CFSTR
from Quartz import CGImageCreate
from Quartz import CGImageDestinationAddImage
from Quartz import CGImageDestinationFinalize
from Quartz import CGPDFDataFormatRaw
from Quartz import CGPDFDataFormatJPEGEncoded
from Quartz import CGPDFDocumentGetPage
from Quartz import CFURLCreateFromFileSystemRepresentation
from Quartz import CGPDFDocumentCreateWithURL
from Quartz import CGPDFDocumentGetNumberOfPages
from Quartz import CGPDFPageGetDictionary
from Quartz import CGPDFDictionaryGetDictionary
from Quartz import CGPDFDictionaryGetCount
from Quartz import CGPDFDictionaryApplyFunction
from Quartz import CGDataProviderCreateWithCFData
from Quartz import CGPDFObjectGetType
from Quartz import CGPDFObjectGetValue
from Quartz import CGPDFDictionaryGetStream
from Quartz import CGPDFDictionaryGetName
from Quartz import CGPDFStreamGetDictionary
from Quartz import CGPDFStreamCopyData
from Quartz import CFURLCreateWithFileSystemPath
from Quartz import CGPDFDictionaryGetInteger
from Quartz import CGPDFDictionaryGetBoolean
from Quartz import CGColorSpaceCreateDeviceRGB
from Quartz import CGPDFDictionaryGetArray
from Quartz import CGColorSpaceGetNumberOfComponents
from Quartz import CGColorSpaceCreateDeviceRGB
from Quartz import CGColorSpaceCreateDeviceCMYK
from Quartz import CGColorSpaceCreateDeviceGray
from Quartz import CGImageDestinationCreateWithURL
from Quartz import CFURLWriteDataAndPropertiesToResource

from Quartz import PDFDocument
from Quartz import NSMakeRange
from Quartz import NSDocumentTypeDocumentAttribute
from Quartz import NSHTMLTextDocumentType 
from Quartz import NSRTFTextDocumentType
from Quartz import NSViewZoomDocumentAttribute
from Quartz import NSPlainTextDocumentType
from Quartz import NSCharacterEncodingDocumentAttribute
from Quartz import NSUTF8StringEncoding

#########################

__all__ = ['extract_images']

#########################
		
def _expand_and_create(outdir):
	outdir = os.path.expanduser(outdir)
	if not os.path.exists(outdir):
		os.makedirs(outdir)
	return outdir

def _create_url(source):
	return CFURLCreateFromFileSystemRepresentation(None, source, len(source), False )

# ----------------------

class _ImageApplierInfo():
	def __init__(self, outdir, chart_ext = '.png'):
		self.page_idx = 0
		self.image_cnt = 0
		self.outdir = outdir
		self.xobj_dict = None
		self.chart_ext = chart_ext = chart_ext or '.png'
		
def _save_raw_image(data_ref, strm_dict, key, info):
	
	rsp, width = CGPDFDictionaryGetInteger( strm_dict, "Width",	None )
	if not rsp: return
	
	rsp, height = CGPDFDictionaryGetInteger( strm_dict, "Height", None )
	if not rsp: return
	
	rsp, bps = CGPDFDictionaryGetInteger( strm_dict, "BitsPerComponent", None )
	if not rsp: return
	
	rsp, interpolation = CGPDFDictionaryGetBoolean( strm_dict, "Interpolate", None )
	if not rsp:
		interpolation = 0

	rendering_intent = kCGRenderingIntentDefault;
	data_provider = CGDataProviderCreateWithCFData(data_ref)
	cg_color_space = None
	
	rsp, _ = CGPDFDictionaryGetArray(strm_dict, "ColorSpace", None)
	if  rsp:
		cg_color_space = CGColorSpaceCreateDeviceRGB()
		spp = CGColorSpaceGetNumberOfComponents(cg_color_space)
	else:
		spp = 1
		rsp, color_space_name = CGPDFDictionaryGetName(strm_dict, "ColorSpace", None)
		if rsp:
			if color_space_name ==  "DeviceRGB":
				cg_color_space = CGColorSpaceCreateDeviceRGB()
				spp = 3
			elif color_space_name == "DeviceCMYK":
				cg_color_space = CGColorSpaceCreateDeviceCMYK()
				spp = 4
			elif color_space_name == "DeviceGray":
				cg_color_space = CGColorSpaceCreateDeviceGray()
			elif bps == 1:  # if there's no colorspace entry, there's still one we can infer from bps
				cg_color_space = CGColorSpaceCreateDeviceGray()
		
	cg_color_space =  cg_color_space or CGColorSpaceCreateDeviceRGB()
	decode_values = None 
	
	row_bits = bps * spp * width;
	row_bytes = row_bits / 8;
	
	# pdf image row lengths are padded to byte-alignment
	if row_bits % 8 != 0:
		row_bytes += 1
	

	type_name = CFSTR("public" +  info.chart_ext)
	
	cg_image = CGImageCreate(width, height, bps, bps * spp, row_bytes,\
							cg_color_space, 0, data_provider, decode_values, interpolation,\
							rendering_intent)
	
	key = "page-%s-%s-%s%s" % (info.page_idx, key, info.image_cnt, info.chart_ext)
	path = os.path.join(info.outdir, key)
	url = CFURLCreateFromFileSystemRepresentation(None, path, len(path), False )

	dest = CGImageDestinationCreateWithURL(url, type_name, 1, None)
	if dest:
		CGImageDestinationAddImage(dest, cg_image, None)
		CGImageDestinationFinalize(dest)
			
def _img_extracter_applier(key, value, info):
	"""
	key: dict key
	value: object reference
	info: context info
	"""
	
	# There seems to be a bug where the value is None
	# so we need to get the stream from the xObject dict
	# which we are passing
	
	rsp, stream = CGPDFDictionaryGetStream( info.xobj_dict, key, None )
	if not rsp:
		return
	
	strm_dict = CGPDFStreamGetDictionary( stream );
	rsp, subtype = CGPDFDictionaryGetName(strm_dict, "Subtype" , None)
	if not rsp or subtype != "Image":
		return
	
	dr, fmt = CGPDFStreamCopyData(stream, None)
	if fmt == CGPDFDataFormatRaw:
		_save_raw_image(dr, strm_dict, key, info)
	else:
		ext = "jpg" if fmt == CGPDFDataFormatJPEGEncoded else "jp2"
		key = "page-%s-%s-%s.%s" % (info.page_idx, key, info.image_cnt, ext)
		path = os.path.join(info.outdir, key)
		url = CFURLCreateFromFileSystemRepresentation(None, path, len(path), False )
		CFURLWriteDataAndPropertiesToResource(url, dr, None, None);
		
	info.image_cnt += 1

def extract_images(pdf_file, outdir, chart_ext = '.png'):
	
	pdf_file = os.path.expanduser(pdf_file)
	if not os.path.exists(pdf_file):
		print "`%s' does not exists" % pdf_file
		return
		
	url = _create_url(pdf_file)
	outdir = _expand_and_create(outdir)
		
	document = CGPDFDocumentCreateWithURL (url)
	count = CGPDFDocumentGetNumberOfPages (document)
	
	print "%s has %s pages" % (pdf_file, count)
	
	info = _ImageApplierInfo(outdir, chart_ext)
	
	for page_idx in xrange(1, count+1):
		
		page = CGPDFDocumentGetPage (document, page_idx)
		page_dict = CGPDFPageGetDictionary( page );

		rsp, resources = CGPDFDictionaryGetDictionary( page_dict, 'Resources', None )
		if not rsp:
			continue

		rsp, xobj_dict = CGPDFDictionaryGetDictionary( resources, "XObject", None )
		if not rsp:
			continue
		
		info.page_idx = page_idx
		info.xobj_dict = xobj_dict
		
		CGPDFDictionaryApplyFunction(xobj_dict, _img_extracter_applier, info)

# ----------------------

def extract_pages(pdf_file, outdir):
	
	pdf_file = os.path.expanduser(pdf_file)
	if not os.path.exists(pdf_file):
		print "`%s' does not exists" % pdf_file
		return
		
	url = _create_url(pdf_file)
	outdir = _expand_and_create(outdir)
	document = PDFDocument.alloc().initWithURL_( url )
	count = document._.pageCount
	
	print "%s has %s pages" % (pdf_file, count)
	
	for page_idx in xrange(count):
		page = document.pageAtIndex_( page_idx )
		atstring = page.attributedString()
		
		if not atstring:
			print "%s is an empty page" % page_idx
			continue
		
		atdata = atstring.RTFFromRange_documentAttributes_(
										 NSMakeRange( 0, atstring.length() ),
										{ NSDocumentTypeDocumentAttribute:  NSHTMLTextDocumentType,
										  NSCharacterEncodingDocumentAttribute: NSUTF8StringEncoding} )
		
		key = "page-%s.rtf" % (page_idx + 1)
		path = os.path.join(outdir, key)
		
		atdata.writeToFile_atomically_(path, False)
		
if __name__ == "__main__":
	#extract_images("~csanchez/Downloads/msw.pdf", "~csanchez/Downloads/images")
	extract_pages("~csanchez/Downloads/msw.pdf", "~csanchez/Downloads/rtfs")