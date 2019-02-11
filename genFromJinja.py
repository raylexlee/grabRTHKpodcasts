#!/usr/bin/python3
import datetime
import os
import hkDateTime
import jinja2
from __slides__ import frontpageContext
from jinja2 import Template
frontpageContext['posting_date']=datetime.datetime.now().strftime(hkDateTime.hktFormat)
html_jinja_env = jinja2.Environment(
	trim_blocks = True,
	lstrip_blocks = True,
	autoescape = False,
	loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)
template = html_jinja_env.get_template('frontpage_template.j2')
print(template.render(frontpageContext))
