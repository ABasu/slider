#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2012 Anupam Basu <prime.lens@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

""" Generates linked slideshow from a list of files."""

__author__ = 'Anupam Basu'
__email__ = 'prime.lens@gmail.com'
__copyright__ = 'Anupam Basu'
__license__ = 'GPL'
__version__ = '3.0' 


try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

from xml.dom.minidom import parseString
import re
import os
from subprocess import Popen, PIPE

################################################################################
def build_slides(slidelist, css, slidename_prefix):
	"""Read the list of slides and process the files into a slideshow."""

	if not os.path.isfile(slidelist):
		print("Can't file the slide list. Please make sure the file exists. Type `slider --help` for a complete list of options.")
		exit(0)

	if not re.search(r'\.css$', css):			# make sure css file has proper extension
		css = css + '.css'
	
	slides = open(slidelist, "r").readlines()
	# Handle newlines, blank lines etc - # begins a comment
	slides = [slide.strip() for slide in slides if slide.strip() != '' and slide.strip()[0] != '#']		

	print("Processing %i slides." % (len(slides)))

	for number, slide in enumerate(slides):
		parse_slide(slide, slidename_prefix, number, len(slides), css)
		# parse_slide(slide, previous, next, number + 1)

	if os.path.isfile(css):
		overwrite = raw_input('The CSS stylesheet already exists. Overwrite? (Y/N):').lower().strip()
		if overwrite == 'y':
			write_css(css)
	else:
		write_css(css)

################################################################################
def parse_slide(slide_file, slidename_prefix, slide_no, no_of_slides, css_file):
	"""Parse individual slides and insert the link nodes"""
	
	# Does the file exist?
	if not os.path.isfile(slide_file):
		print("Can't find the slide: %s. Make sure the file exists." % (slide_file))
		return

	markdown = re.search("(\S*)\.md$", slide_file)
	image = re.search('(\S*)(\.jpg$|\.jpeg|\.png|\.gif|\.svg)', slide_file)
	html = re.search('(\S*)\.html?$', slide_file)

	# Handle different filetypes and generate a 'root' object
	if markdown:
		html_string = markdown_to_html(slide_file)
		if html_string:
			root = ET.fromstring(html_string)
		else:
			print("Can't process markdown slide: %s. Make sure either `Markdown.pl` or `pandoc` is installed." % (slide_file))
			return
	elif image:				
		html_string = image_to_html(slide_file)
		if html_string:
			root = ET.fromstring(html_string)
		else:
			print("Can't process the image: %s." % (slide_file))
	elif html:
		try:
			tree = ET.parse(slide_file)
			root = tree.getroot()
		except ET.ParseError:
			print("Couldn't parse slide: %s. Make sure it is valid XHTML." % (slide_file))
			return
	else:
		print("Couldn't recognize the file: %s" % (slide_file))
		return

	# Find the body tag and insert the links
	body = root.find('body')
	current_name = slidename_prefix + '_' + str(slide_no + 1).zfill(3) + '.html'
	prev_name = slidename_prefix + '_' + str(slide_no).zfill(3) + '.html'
	next_name = slidename_prefix + '_' + str(slide_no + 2).zfill(3) + '.html'

	# Insert links only if they don't already exist
	if slide_no != 0:
		div = ET.SubElement(body, "div")
		div.attrib['id'] = 'slider_prev'
		link = ET.SubElement(div, "a")
		link.attrib['href'] = prev_name
		link.text = '<'

	if slide_no != no_of_slides - 1:
		div = ET.SubElement(body, "div")
		div.attrib['id'] = 'slider_next'
		link = ET.SubElement(div, "a")
		link.attrib['href'] = next_name
		link.text = '>'
	
	# Link the stylesheet
	head = root.find('head')
	css = ET.SubElement(head, 'link')
	css.attrib['href'] = css_file
	css.attrib['rel'] = 'stylesheet'
	css.attrib['type'] = 'text/css'

	# Wrap the whole body in a div
	div1 = ET.Element('div', {'class': 'slider'})
	for element in list(body.getchildren()):
		div1.append(element)
		body.remove(element)
		div1.text, body.text = body.text, ''
		div1.tail, body.tail = body.tail, ''
	body.append(div1)

	root_string = re.sub(r'\n\s*\n', r'', ET.tostring(root))
	root_string = parseString(root_string).toprettyxml(encoding = 'utf-8')
	root = ET.fromstring(root_string)

	ET.ElementTree(root).write(current_name, method = 'html')
	print("Processed slide: %s" % (slide_file))

################################################################################
def image_to_html(img_file):
	"""Create html boilerplate, wrap around the image and return html string."""

	html_output = '<html><head><title>' + img_file + '</title></head><body class="image_slide"><table id="slider_table"><tr><td><img id="slider" src = "' + img_file + '"/></td></tr></table></body></html>'
	return html_output

################################################################################
def markdown_to_html(md_file):
	"""Use a markdown processor to generate HTML from the markdown file.
	   Return an HTML string if successful."""

	try:
		# Run Markdown.pl - route screen output to a string
		html_output = Popen(["Markdown.pl", md_file], stdout = PIPE).communicate()[0]
	except OSError:
		try:
			# Run pandoc - route screen output to string
			html_output = Popen(["pandoc", md_file], stdout = PIPE).communicate()[0]
		except OSError:
			return

	# Add HTML boilerplate, and a file title plus tag is as a markdown file for css
	html_output = '<html><head><title>' + md_file + '</title></head><body class="markdown_slide"><table id="slider_table"><tr><td>' + html_output + '</td></tr></table></body></html>'
	return html_output

################################################################################
def write_css(css):
	"""Write the CSS file to style the slideshow."""

	css_string = ("body { background:black; color:darkgray; font-family:'Unna', baskerville, garamond, times, times new roman, serif; text-align:left; }"
					".slider { margin:0px auto; width: 1000px; }"
					"#slider_next { float:right; position:absolute; right:0; top:50%; }"
					"#slider_prev { float:left; position:absolute; left:0; top:50%; }"
					"#slider_next a, #slider_prev a { color:#2f2f2f; font-size:30pt; text-decoration:none; }"
					"img#slider { border:0px solid black; display:block; margin-left:auto; margin-right:auto; width:1000px; box-shadow:4px 4px 8px #000; }"
					"#slider_table { height:100%; width:100%; }"
					"#slider_table td { vertical-align: middle; }")

	# Format the css file
	css_string = re.sub(r'({|}|;)', r'\1\n', css_string)
	css_string = re.sub(r'(})', r'\1\n', css_string)
	css_string = re.sub(r'\n (\S)', r'\n\t\1', css_string)

	file = open(css, "w")
	file.write(css_string)
	file.close()

################################################################################
# Main body begins here
################################################################################
if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description = 'Connect images, markdown files, and html documents into a linked slideshow.')
	parser.add_argument('-s', '--slides', action = 'store', nargs = 1, default = ['slider.txt'], help = 'Text file containing a list of slides (default: slider.txt).')
	parser.add_argument('-c', '--css', action = 'store', nargs = 1, default = ['slider.css'], help = 'Stylesheet for the slides (default: slider.css).')
	parser.add_argument('-n', '--slideprefix', action = 'store', nargs = 1, default = ['slider'], help = 'Name prefix for the slide files (default: slider - generates slider_001.html etc.)')

	args = parser.parse_args()
	build_slides(args.slides[0], args.css[0], args.slideprefix[0])

