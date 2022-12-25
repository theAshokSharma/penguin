from datetime import date
from dataclasses import dataclass

from fhirclient.models.condition import Condition

# https://hl7.org/fhir/condition.html
# https://patient-browser.smarthealthit.org/#/patient/2

@dataclass
class PatientCondition:
    clinicalStatus: str
    verificationStatus: str
    severity: str
    condition: str
    onsetStart: date
    onsetEnd: date
    recordedDate: date

    @classmethod
    def fromFHIRCondition(cls, cnd: Condition):
        status = cnd.clinicalStatus.text
        verStatus = cnd.verificationStatus.text if cnd.verificationStatus is not None else ""
        condition = cnd.code.text if cnd.code is not None else ""
        recDate = cnd.recordedDate.isostring if cnd.recordedDate is not None else None
        onsetStart = cnd.onsetPeriod.start.isostring if cnd.onsetPeriod is not None else None
        onsetEnd = cnd.onsetPeriod.end.isostring if cnd.onsetPeriod is not None else None
        severity = cnd.severity

        return cls(clinicalStatus=status,
                   verificationStatus=verStatus,
                   severity=severity,
                   condition=condition,
                   onsetStart=onsetStart,
                   onsetEnd=onsetEnd,
                   recordedDate=recDate)

    def toString(self):
        return "Date:{0}  {1} Clinical Status: {2}  Verification Status:{3}".format(
            self.recordedDate,
            self.condition,
            self.clinicalStatus,
            self.verificationStatus)

    @staticmethod
    def get_conditions(smart):
        if smart is None:
            return None

        resources = Condition.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome' and
            src.clinicalStatus is not None]
        return resources_

    @staticmethod
    def get_patientConditions(smart):
        cnds = PatientCondition.get_conditions(smart)

        if cnds is None:
            return None

        patientcnds = []

        for cnd in cnds:
            patientcnd = PatientCondition.fromFHIRCondition(cnd)
            patientcnds.append(patientcnd)

        return patientcnds
