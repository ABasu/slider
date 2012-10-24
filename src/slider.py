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

	for number, slide in enumerate(slides):
		if number == 0:
			previous = ""
		if number == len(slides) - 1:
			next = ""
		if number > 0:
			previous = slides[number - 1]
		if number < len(slides) - 1:
			next = slides[number + 1]

		parse_slide(slide.rstrip(), previous.rstrip(), next.rstrip())

################################################################################
def parse_slide(slide_file, prev, next):
	"""Parse individual slides and insert the link nodes"""
	
	if not os.path.isfile(slide_file):
		print("Can't find the slide: %s. Make sure the file exists." % (slide_file))
		return

	if re.match('\S*.md$', prev):
			prev = prev.rstrip('.md') + '.html'			# Change the name of the file to html
	if re.match('\S*.md$', next):
			next = next.rstrip('.md') + '.html'			# Change the name of the file to html

	# if the slide is a Markdown file, generate the html version and wrap in HTML boilerplate
	if re.match('\S*.md$', slide_file):
		html = markdown_to_html(slide_file)
		if html:
			root = ET.fromstring(html)
			slide_file = slide_file.rstrip('.md') + '.html'			# Change the name of the file to html
		else:
			print("Can't process markdown slide: %s. Make sure either `Markdown.pl` or `pandoc` is installed." % (slide_file))
			return
	else:			# if the slide is an XHTML file, parse it
		try:
			tree = ET.parse(slide_file)
			root = tree.getroot()
		except ET.ParseError:
			print("Couldn't parse slide: %s. Make sure it is valid XHTML." % (slide_file))
			return

	# Find the body tag and insert the links
	body = root.find('body')

	# Link the stylesheet - if it doesn't already exist
	if root.find(".//head[@href='slider.css']") is None:
		head = root.find('head')
		css = ET.SubElement(head, 'link')
		css.attrib['href'] = 'slider.css'
		css.attrib['rel'] = 'stylesheet'
		css.attrib['type'] = 'text/css'
	

	# Insert links only if they don't already exist
	if root.find(".//div[@id='slider_prev']") is None and prev != "":
		div = ET.SubElement(body, "div")
		div.attrib['id'] = 'slider_prev'
		link = ET.SubElement(div, "a")
		link.attrib['href'] = prev
		link.text = '<'

	if root.find(".//div[@id='slider_next']") is None and next != "":
		div = ET.SubElement(body, "div")
		div.attrib['id'] = 'slider_next'
		link = ET.SubElement(div, "a")
		link.attrib['href'] = next
		link.text = '>'
	
	ET.ElementTree(root).write(slide_file)


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
	html_output = '<html><head><title>' + md_file + '</title></head><body class="markdown">' + html_output + '</body></html>'
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

