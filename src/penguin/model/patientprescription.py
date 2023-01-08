from datetime import date
from dataclasses import dataclass

from fhirclient.models.condition import Condition
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest

# https://hl7.org/fhir/medicationrequest.html
# https://patient-browser.smarthealthit.org/#/patient/2

# WORK IN PROGESS

@dataclass
class PatientPrescription:
    medication: str
    priority: str
    authored_on: date
    performer: str
    requester: str
    number_of_repeats: str
    supply_duration_value: str
    supply_duration_unit: str
    quantity_value: str
    quantity_unit: str
    dosage_instructions: str


    @classmethod
    def fromFHIRCondition(cls, medreq: MedicationRequest):
        medication = medreq.medicationReference.display if medreq.medicationReference is not None else None
        priority = medreq.priority
        authored_on = medreq.authoredOn.isostring
        performer = medreq.performer.display if medreq.performer is not None else None
        requester = medreq.requester.display if medreq.requester is not None else None
        number_of_repeats = medreq.dispenseRequest.numberOfRepeatsAllowed

        return cls(medication=medication,
                   priority=priority,
                   authored_on=authored_on,
                   performer=performer,
                   requester=requester,
                   number_of_repeats=number_of_repeats)

    def toString(self):
        return "Date:{0}  {1} Clinical Status: {2}  Verification Status:{3}".format(
            self.recordedDate,
            self.condition,
            self.clinicalStatus,
            self.verificationStatus)

    @staticmethod
    def get_presecriptions(smart):
        if smart is None:
            return None

        resources = MedicationRequest.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        return resources_

    @staticmethod
    def get_patient_presecriptions(smart):
        pres = PatientPrescription.get_presecriptions(smart)

        if pres is None:
            return None

        patientpres = []

        for itm in pres:
            patientitm = PatientPrescription.fromFHIRCondition(itm)
            patientpres.append(patientitm)

        return patientpres
