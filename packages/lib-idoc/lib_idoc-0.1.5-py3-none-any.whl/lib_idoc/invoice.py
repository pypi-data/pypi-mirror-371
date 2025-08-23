import re
import logging
import xmlschema
from pathlib import Path
from lib_invoice import Invoice

from lib_utilys import clean_special_characters, clean_xml

logger = logging.getLogger(__name__)

class IDOC:
    def __init__(self, startseg_path: Path, dynseg_path: Path, endseg_path: Path):
        self.static_segment_start = None
        self.static_segment_end = None
        self.dynamic_segment = None
        self.xml_filename = None
        self.xml = None
        self._initialize_segments(startseg_path, dynseg_path, endseg_path)

    def _initialize_segments(self, startseg_path: Path, dynseg_path: Path, endseg_path: Path):
        """Initializes IDOC segments."""
        with open(startseg_path, 'r') as file:
            self.static_segment_start = file.read()
        with open(dynseg_path, 'r') as file:
            self.dynamic_segment = file.read()
        with open(endseg_path, 'r') as file:
            self.static_segment_end = file.read()

    def _replace_static_start(self, kvpairs: dict):
        """Replaces the static start segment of the IDOC."""
        for key, value in kvpairs.items():
            if value is not None:
                self.static_segment_start = self.static_segment_start.replace(f"[{key}]", str(value))
        self.static_segment_start = re.sub(r'\[.*?\]', '', self.static_segment_start)

    def _replace_dynamic(self, kvpairs: dict):
        """Replaces the dynamic segment of the IDOC."""
        dynamic, position_counter = '', 10
        for material in kvpairs['Material_list']:
            template = self.dynamic_segment
            for key, value in material.items():
                if value is not None:
                    template = template.replace(f"[{key}]", str(value))
            template = template.replace('[Position_number]', str(position_counter))
            template = re.sub(r'\[.*?\]', '', template)
            position_counter += 10
            dynamic += template
        self.dynamic_segment = dynamic


    def _replace_static_end(self, kvpairs: dict):
        """Replaces the static end segment of the IDOC."""
        for key, value in kvpairs.items():
            if value is not None:
                self.static_segment_end = self.static_segment_end.replace(f"[{key}]", str(value))
        self.static_segment_end = re.sub(r'\[.*?\]', '', self.static_segment_end)

    def _configure_filename(self, invoice: Invoice):
        """Configures the filename of the IDOC."""
        self.xml_filename = f"{invoice.kvpairs['Creditor_number']}-{invoice.kvpairs['Debtor_international_location_number']}.{invoice.kvpairs['Invoice_number']}.xml"
        self.xml_filename = clean_special_characters(self.xml_filename)

    def configure_idoc(self, invoice: Invoice):
        """Creates the IDOC."""
        self._configure_filename(invoice)
        self._replace_static_start(invoice.kvpairs)
        self._replace_dynamic(invoice.kvpairs)
        self._replace_static_end(invoice.kvpairs)
        self.xml = self.static_segment_start + self.dynamic_segment + self.static_segment_end
        self.xml = clean_xml(self.xml)
        validate = xmlschema.validate(self.xml)
