
import requests
from jinja2 import Environment, FileSystemLoader

class TallyClient:
    def __init__(self, url="http://localhost:9000", template_dir="xml_templates"):
        self.url = url
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def post_xml(self, xml_str):
        headers = {'Content-Type': 'text/xml'}
        response = requests.post(self.url, data=xml_str.encode(), headers=headers)
        return response.text
