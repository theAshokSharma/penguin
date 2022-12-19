from datetime import date
from dataclasses import dataclass

from fhirclient.models.condition import Condition


@dataclass
class PatientCondition:
    clinicalStatus: str
    verificationStatus: str
    category: str
    severity: str
    code: str
    bodySite: str
    subject: str
    onset: str
    abatement: str
    recordedDate: date

    @classmethod
    def fromFHIRCondition(cls, cnd: Condition):
        pass

    @staticmethod
    def get_conditions(smart):
        if smart is None:
            return None

        resources = Condition.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome' and
            src.clinicalStatus is not None]
        return resources_
