#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'Anupam Basu (prime.lens@gmail.com)'
__version__ = '.5' 

import xml.etree.cElementTree as ET
import re
import os
from subprocess import Popen, PIPE

################################################################################
def build_slides(slidelist):
	"""Read the list of slides and process the files into a slideshow."""

	if not os.path.isfile(slidelist):
		print("Can't file the slide list. Please make sure the file exists.")
		exit(0)
	
	slides = open(slidelist, "r").readlines()
	# Handle newlines, blank lines etc - # begins a comment
	slides = [slide.strip() for slide in slides if slide.strip() != '' and slide.strip()[0] != '#']		

	# Check to see if there are filenames that might clash 
	filenames = [re.search('(\S*)\.\S*', filename).group(1) for filename in slides]
	if len(slides) != len(set(filenames)):
		print "There seem to be duplicate filenames. Please check all slide names(not including extension) are unique."
		exit(0)

	print("Processing %i slides." % (len(slides)))

	for number, slide in enumerate(slides):
		if number == 0:
			previous = ""
		if number == len(slides) - 1:
			next = ""
		if number > 0:
			previous = slides[number - 1]
		if number < len(slides) - 1:
			next = slides[number + 1]

		parse_slide(slide, previous, next)

################################################################################
def parse_slide(slide_file, prev, next):
	"""Parse individual slides and insert the link nodes"""
	
	# Does the file exist?
	if not os.path.isfile(slide_file):
		print("Can't find the slide: %s. Make sure the file exists." % (slide_file))
		return

	# if the previous or next slides were not html, fix their extensions for writing out
	markdown = re.search("(\S*)\.md$", prev)
	image = re.search('(\S*)(\.jpg$|\.jpeg|\.png|\.gif)', prev)
	if markdown:
		prev = markdown.group(1) + '.html'
	elif image:
		prev = image.group(1) + '.html'

	markdown = re.search("(\S*)\.md$", next)
	image = re.search('(\S*)(\.jpg$|\.jpeg|\.png|\.gif)', next)
	if markdown:
		next = markdown.group(1) + '.html'
	elif image:
		next = image.group(1) + '.html'


	markdown = re.search("(\S*)\.md$", slide_file)
	image = re.search('(\S*)(\.jpg$|\.jpeg|\.png|\.gif)', slide_file)
	html = re.search('(\S*)\.html?$', slide_file)

	# if the slide is a Markdown file, generate the html version and wrap in HTML boilerplate
	if markdown:
		html_string = markdown_to_html(slide_file)
		if html_string:
			root = ET.fromstring(html_string)
			slide_file = markdown.group(1) + '.html'			# Change the name of the file to html
		else:
			print("Can't process markdown slide: %s. Make sure either `Markdown.pl` or `pandoc` is installed." % (slide_file))
			return
	# If it's an image, generate HTML boilerplate
	elif image:
		html_string = image_to_html(slide_file)
		if html_string:
			root = ET.fromstring(html_string)
			slide_file = image.group(1) + '.html'				# Change the name of the file to html
		else:
			print("Can't process the image: %s." % (slide_file))
	# if the slide is an XHTML file, parse it
	elif html:
		try:
			tree = ET.parse(slide_file)
			root = tree.getroot()
		except ET.ParseError:
			print("Couldn't parse slide: %s. Make sure it is valid XHTML." % (slide_file))
			return
	# Otherwise, we don't know what to do with the file
	else:
		print("Couldn't recognize the file: %s" % (slide_file))
		return

	# Find the body tag and insert the links
	body = root.find('body')

	if root.find(".//div[@class='slider']") is None:
		# Insert links only if they don't already exist
		if prev != "":
			div = ET.SubElement(body, "div")
			div.attrib['id'] = 'slider_prev'
			link = ET.SubElement(div, "a")
			link.attrib['href'] = prev
			link.text = '<'

		if next != "":
			div = ET.SubElement(body, "div")
			div.attrib['id'] = 'slider_next'
			link = ET.SubElement(div, "a")
			link.attrib['href'] = next
			link.text = '>'
		
		# Link the stylesheet - if it doesn't already exist
		if root.find(".//head[@href='slider.css']") is None:
			head = root.find('head')
			css = ET.SubElement(head, 'link')
			css.attrib['href'] = 'slider.css'
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
	else:
		print("The file has already been converted to a slide: %s. To redo, undo slides first." % (slide_file))
		return

	ET.ElementTree(root).write(slide_file)
	print("Processed slide: %s" % (slide_file))

################################################################################
def image_to_html(img_file):
	"""Create html boilerplate, wrap around the image and return html string."""

	html_output = '<html><head><title>' + img_file + '</title></head><body class="image_slide"><img id="slider" src = "' + img_file + '"/></body></html>'
	return html_output

################################################################################
def markdown_to_html(md_file):
	"""Use a markdown processor to generate HTML from the markdown file.
	   Return an HTML string if successful."""

	try:
		# Run pandoc - route screen output to string
		html_output = Popen(["pandoc", md_file], stdout = PIPE).communicate()[0]
	except OSError:
		try:
			# Run Markdown.pl - route screen output to a string
			html_output = Popen(["Markdown.pl", md_file], stdout = PIPE).communicate()[0]
		except OSError:
			return

	# Add HTML boilerplate, and a file title plus tag is as a markdown file for css
	html_output = '<html><head><title>' + md_file + '</title></head><body class="markdown_slide">' + html_output + '</body></html>'
	return html_output




################################################################################
# Main body begins here
################################################################################
if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description = 'Connect html documents into a linked set of slides')
	parser.add_argument('-s', '--slides', action = 'store', nargs = 1, default = 'slides.txt', help = 'Build the slides.')

	args = parser.parse_args()
	build_slides(args.slides)

