from datetime import date
from dataclasses import dataclass

from fhirclient.models.allergyintolerance import AllergyIntolerance

# https://build.fhir.org/immunization.html


@dataclass
class PatientAllergies:
    lastOccurrence: date
    status: str
    verificationStatus: str
    type: str
    category: str
    code: str
    criticality: str
    onsetDateTime: date
    recordedDate: date
    note: str
# list of reactions
    @classmethod
    def fromFHIRAllergies(cls, alz: AllergyIntolerance):
        status = alz.clinicalStatus
        verificationStatus = alz.verificationStatus
        type = alz.type
        category = alz.category
        code = alz.code
        criticality = alz.criticality
        lastOccurrence = alz.lastOccurrence.isostring
        onsetDateTime = alz.onsetDateTime
        recordedDate = alz.recordedDate.isostring
        note = alz.note
        return cls(status=status,
                   verificationStatus=verificationStatus,
                   type=type,
                   category=category,
                   code=code,
                   criticality=criticality,
                   lastOccurrence=lastOccurrence,
                   onsetDateTime=onsetDateTime,
                   recordedDate=recordedDate,
                   note=note)

    def toString(self):
        return "Date: {0} code: {1}  status: {2} verification:{3} criticality:{4} notes: {5}".format(
            self.lastOccurrence,
            self.code,
            self.status,
            self.verificationStatus,
            self.criticality,
            self.note)

    @staticmethod
    def _get_allergies(smart):
        if smart is None:
            return None

        try:
            resources = AllergyIntolerance.where(struct={'patient': smart.patient_id}).\
                perform_resources(smart.server)

            resources_ = [src for src in resources if src.resource_type != 'OperationOutcome' and
                src.status == 'completed']
        except Exception as e:
            resources_ = None

        return resources_

    @staticmethod
    def get_patientAllergies(smart):
        alzs = PatientAllergies._get_allergies(smart)

        if alzs is None:
            return None

        patientalzs = []

        for alz in alzs:
            patientalz = PatientAllergies.fromFHIRAllergies(alz)
            patientalzs.append(patientalz)

        patientalzs.sort(key=lambda x: x.lastOccurrence, reverse=True)
        return patientalzs
