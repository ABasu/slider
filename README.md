slider.py - A Barebones Slideshow Generator
===========================================

Slider lets you connect individual images, markdown files and html documents into a slide show. Slides can be as simple as a single image or some bare text in markdown format, or as complex as full blown html pages with svg graphics, embedded objects, interactive javascript and HTML5 visualizations. 

There are several JavaScript slideshow generators that let you compile images and text into a single html file and then scroll between frames. These don't fare well if you have multiple slides with complex interactive visualizations - especially ones that load a lot of data - because all slides get loaded in the background at once. Slider steps out of the way by essentially making each slide a stand-alone html file that is simply linked to the previous and next slides. In fact it leaves your original source files untouched. You can make slides as simple as you want (bare text or an image) but also scale up to as complex as you want as well. The only restriction is the main source files (images, .md files or .html files) need to be in the same directory. 

Usage
-----

Slider accepts a text file (default: slider.txt) with a simple list of slides and generates a linked slideshow from them. The slide list can contain comment lines starting with `#` and blank lines along with the ordered list of files to be linked in the slideshow. An example:

		# Introduction
		title_graphic.jpg
		intro_slide.md

		# Main Argument
		interactive_d3_slide.html
		data_graph.png
		protovis_slide.html

		# conclusion
		bullet_list_summary.md
		final_slide.md
		closing_graphic.jpg

Putting this in a file called `slider.txt` in the same directory as these files and calling `slider.py` will generate a set of files named `slide_001.html` through `slide_008.html`. The originals will be left untouched. A stylesheet called `slider.css` will also be generated and you can modify that to change the look of the slideshow.

Individual slides can be in one of te following formats:

* [Markdown](http://daringfireball.net/projects/markdown/syntax) files - you need to have either [Markdown.pl](http://daringfireball.net/projects/markdown/) or [pandoc](http://johnmacfarlane.net/pandoc/) installed on your system.
* Image - currently .jpg, .gif, and .png are supported.
* Html file - this can be any html file including scripts, interactive visualizations, embedded objects etc. (Note: _The files need to be fully XML compliant._)

To modify the names of the list or css files or to change the prefix of the slide files, use the following options:

		usage: slider.py [-h] [-s SLIDES] [-c CSS] [-n SLIDENAME]

		optional arguments:
		  -h, --help            					show this help message and exit
		  -s SLIDES, --slides SLIDES 				Text file containing a list of slides (default: slider.txt).
		  -c CSS, --css CSS     					Stylesheet for the slides (default: slider.css).
		  -n SLIDEPREFIX, --slideprefix SLIDEPREFIX	Name prefix for the slide files (default: slider - generates slider_001.html etc).



Copyright (C) 2012 Anupam Basu <prime.lens@gmail.com>
