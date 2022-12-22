
from dataclasses import dataclass
from datetime import date
from fhirclient.models.patient import Patient
from fhirclient.models.address import Address
from fhirclient.models.contactpoint import ContactPoint

"""
Class to manage Patient data structure
"""

address_component = ['line1', 'line2', 'city', 'state', 'zip_code', 'country']


@dataclass
class PatientInfo:

    patientID: str
    given_name: str
    family_name: str
    gender: str
    birth_date: date
    phone_mobile: str
    phone_home: str
    phone_work: str
    email: str
    home_address: dict.fromkeys(address_component)
    practitioner: str
    marital_status: str
    preferred_lang: str
    managing_organization: str

    def full_name(self) -> str:
        return self.given_name + " " + self.family_name

    @classmethod
    def fromFHIRPatient(cls, pat: Patient):
        patientID = pat.id
        given_name = " ".join(pat.name[0].given)
        family_name = pat.name[0].family
        gender = pat.gender
        birth_date = pat.birthDate.isostring
        marital_status = pat.maritalStatus.text if pat.maritalStatus is not None else None
        preferred_lang = pat.language
        practitioner = pat.generalPractitioner[0].display \
            if pat.generalPractitioner is not None else None
        managing_organization = pat.managingOrganization.display \
            if pat.managingOrganization is not None else None
        address = [PatientInfo._parse_address(addr)
                for addr in pat.address if addr.use == 'home']
        # convert it into dict
        home_address = dict.fromkeys(address_component)
        for addr in address:
            home_address.update(addr)
        phone_home = PatientInfo._get_contact(pat.telecom, 'phone', 'home')
        phone_mobile = PatientInfo._get_contact(pat.telecom, 'phone', 'mobile')
        phone_work = PatientInfo._get_contact(pat.telecom, 'phone', 'work')
        email = PatientInfo._get_contact(pat.telecom, 'email', None)
        
        return cls(patientID, given_name, family_name, gender, birth_date, phone_mobile, phone_home,
        phone_work, email, home_address, practitioner, marital_status, preferred_lang, managing_organization)

    @staticmethod
    def _parse_address(addr: Address) -> dict.fromkeys(address_component):
        address = dict.fromkeys(address_component)
        if addr is not None:
            line1 = addr.line[0] if len(addr.line) > 0 else ""
            line2 = addr.line[1] if len(addr.line) > 1 else ""
            city = addr.city
            state = addr.state
            zip_code = addr.postalCode
            country = addr.country

        address[address_component[0]] = line1
        address[address_component[1]] = line2
        address[address_component[2]] = city
        address[address_component[3]] = state
        address[address_component[4]] = zip_code
        address[address_component[5]] = country
        return address

    @staticmethod
    def _get_contact(contactinfo: ContactPoint, system: str, use: str = None):

        value_to_return = None
        if use is not None:
            value_to_return = ''.join(
                [cntc.value for cntc in contactinfo if cntc.system == system and cntc.use == use])
        else:
            value_to_return = ''.join([cntc.value for cntc in contactinfo if cntc.system == system])
        return value_to_return
