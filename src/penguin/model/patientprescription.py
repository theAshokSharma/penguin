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
    instructions: str
    therapy_course: str
    medication_reason: str
    supply_duration_value: str
    supply_duration_unit: str
    repeats_allowed: str
    validity_start: date = None
    validity_end: date = None

    @classmethod
    def fromFHIRCondition(cls, medreq: MedicationRequest):
        dispense_req: MedicationRequestDispenseRequest = medreq.dispenseRequest
        medication = medreq.medicationReference.display if medreq.medicationReference is not None else None
        priority = medreq.priority
        authored_on = medreq.authoredOn.isostring
        performer = medreq.performer.display if medreq.performer is not None else None
        requester = medreq.requester.display if medreq.requester is not None else None
        instructions = medreq.dosageInstruction[0].patientInstruction
        therapy_course = medreq.courseOfTherapyType.text if medreq.courseOfTherapyType is not None else None
        medication_reason = medreq.reasonCode[0].text if medreq.reasonCode is not None else None
        supply_duration_value = dispense_req.expectedSupplyDuration.value\
            if dispense_req.expectedSupplyDuration is not None else 0
        supply_duration_unit = dispense_req.expectedSupplyDuration.unit\
            if dispense_req.expectedSupplyDuration is not None else ''
        repeats_allowed = dispense_req.numberOfRepeatsAllowed\
            if dispense_req.numberOfRepeatsAllowed is not None else ''

        if dispense_req.validityPeriod is not None:
            validity_start = dispense_req.validityPeriod.start.isostring\
                if dispense_req.validityPeriod.start is not None else None
            validity_end = dispense_req.validityPeriod.end.isostring\
                if dispense_req.validityPeriod.end is not None else None
        return cls(medication=medication,
                   priority=priority,
                   authored_on=authored_on,
                   performer=performer,
                   requester=requester,
                   instructions=instructions,
                   medication_reason=medication_reason,
                   supply_duration_value=supply_duration_value,
                   supply_duration_unit=supply_duration_unit,
                   repeats_allowed=repeats_allowed,
                   validity_start=validity_start,
                   validity_end=validity_end,
                   therapy_course=therapy_course)

    def toString(self):
        return "Date:{0}  {1} instructions: {2}  {3}".format(
            self.validity_start,
            self.medication,
            self.instructions,
            self.therapy_course)

    @staticmethod
    def _get_presecriptions(smart):
        if smart is None:
            return None

        try:
            resources = MedicationRequest.where(struct={'patient': smart.patient_id}).\
                perform_resources(smart.server)

            resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        except Exception as e:
            resources_ = None

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
