from datetime import date
from dataclasses import dataclass

from fhirclient.models.medicationrequest import MedicationRequest
from fhirclient.models.medicationrequest import MedicationRequestDispenseRequest

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
    dispense_req: MedicationRequestDispenseRequest
    instructions: str
    therapy_course: str

    @classmethod
    def fromFHIRCondition(cls, medreq: MedicationRequest):
        dispense_req = medreq.dispenseRequest
        medication = medreq.medicationReference.display if medreq.medicationReference is not None else None
        priority = medreq.priority
        authored_on = medreq.authoredOn.isostring
        performer = medreq.performer.display if medreq.performer is not None else None
        requester = medreq.requester.display if medreq.requester is not None else None
        instructions = medreq.dosageInstruction[0].patientInstruction
        therapy_course = medreq.courseOfTherapyType.text if medreq.courseOfTherapyType is not None else None
        return cls(medication=medication,
                   priority=priority,
                   authored_on=authored_on,
                   performer=performer,
                   requester=requester,
                   dispense_req=dispense_req,
                   instructions=instructions,
                   therapy_course=therapy_course)

    def toString(self):
        return "Date:{0}  {1} Clinical Status: {2}  Verification Status:{3}".format(
            self.recordedDate,
            self.condition,
            self.clinicalStatus,
            self.verificationStatus)

    @staticmethod
    def _get_presecriptions(smart):
        if smart is None:
            return None

        resources = MedicationRequest.where(struct={'patient': smart.patient_id}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        return resources_

    @staticmethod
    def get_patient_presecriptions(smart):
        pres = PatientPrescription._get_presecriptions(smart)

        if pres is None:
            return None

        patientpres = []

        for itm in pres:
            patientitm = PatientPrescription.fromFHIRCondition(itm)
            patientpres.append(patientitm)

        return patientpres
