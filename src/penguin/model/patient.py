
from dataclasses import dataclass
from datetime import date

"""
Class to manage Patient data structure
"""


@dataclass
class Patient:

    given: str
    family: str
    gender: str
    birth_date: date
    phone: str
    email: str
    street_line1: str
    street_line2: str
    city: str
    state: str
    zip_code: str

    def full_name(self):
        return (" ").join(self.given, self.family)