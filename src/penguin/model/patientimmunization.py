from datetime import date
from dataclasses import dataclass

from fhirclient.models.immunization import Immunization

# https://build.fhir.org/immunization.html


@dataclass
class PatientImmunization:
    occurrenceDate: date
    status: str
    vaccineCode: str
    doseQuantityValue: str
    doseQuantityUnit: str
    manufacturer: str
    lotNumber: str
    note: str

    @classmethod
    def fromFHIRImmunization(cls, imz: Immunization):
        status = imz.status
        lot = imz.lotNumber
        imzdate = imz.occurrenceDateTime.isostring
        vacCode = imz.vaccineCode.text if imz.vaccineCode is not None else None
        manufacturer = imz.manufacturer.display if imz.manufacturer is not None else None
        doseQtyValue = imz.doseQuantity.value if imz.doseQuantity is not None else None
        doseQtyUnit = imz.doseQuantity.unit if imz.doseQuantity is not None else None
        note = imz.note
        return cls(status=status,
                   occurrenceDate=imzdate,
                   vaccineCode=vacCode,
                   doseQuantityValue=doseQtyValue,
                   doseQuantityUnit=doseQtyUnit,
                   manufacturer=manufacturer,
                   lotNumber=lot,
                   note=note)

    def toString(self):
        return "Date: {0} Vaccine: {1}  Dose:{2}/{3} Manufacturer: {4} Lot# {5} Status: {6}".format(
            self.occurrenceDate,
            self.vaccineCode,
            self.doseQuantityValue,
            self.doseQuantityUnit,
            self.manufacturer,
            self.lotNumber,
            self.status)

    @staticmethod
    def _get_immunization(smart):
        if smart is None:
            return None

        resources = Immunization.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome' and
            src.status == 'completed']
        return resources_

    @staticmethod
    def get_patientImmunization(smart):
        imzs = PatientImmunization._get_immunization(smart)

        if imzs is None:
            return None

        patientimzs = []

        for imz in imzs:
            patientimz = PatientImmunization.fromFHIRImmunization(imz)
            patientimzs.append(patientimz)

        patientimzs.sort(key=lambda x: x.occurrenceDate, reverse=True)
        return patientimzs
