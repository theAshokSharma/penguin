from datetime import date, datetime
from dataclasses import dataclass

from fhirclient.server import FHIRPermissionDeniedException
from fhirclient.models.diagnosticreport import DiagnosticReport
from fhirclient.models.fhirreference import FHIRReference

# https://hl7.org/fhir/condition.html
# https://patient-browser.smarthealthit.org/#/patient/2

# INCOMPLETE - WORK IN PROGRESS


@dataclass
class PatientDiagnosticReport:
    basedOn: str
    status: str
    category: str
    result: str
    effectiveDateTime: datetime
    effectivePeriod: str

    @classmethod
    def fromFHIRCondition(cls, dr: DiagnosticReport):

        ref: FHIRReference = dr.basedOn[0]
        basedOn = ref.type if ref is not None else ""
        status = dr.status
        category = dr.category[0].text if dr.category is not None else ""
        result = dr.result[0].display if dr.result is not None else ""
        effectiveDateTime = dr.effectiveDateTime.isostring if dr.effectiveDateTime is not None else None
        effectivePeriod = dr.effectivePeriod

        return cls(status=status,
                   basedOn=basedOn,
                   category=category,
                   result=result,
                   effectiveDateTime=effectiveDateTime,
                   effectivePeriod=effectivePeriod)

    def toString(self):
        return "Date:{0} result: {1}  Status:{2}".format(
            self.effectiveDateTime,
            self.result,
            self.status)

    @staticmethod
    def _get_diagnostic_report(smart):
        if smart is None:
            return None

        try:
            resources = DiagnosticReport.where(struct={'patient': smart.patient_id}).\
                perform_resources(smart.server)
        except Exception as e:
            # FHIRPermissionDeniedException:
            return None
        except FHIRPermissionDeniedException as ex:
            return None

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        return resources_

    @staticmethod
    def get_patient_diagnostic_report(smart):
        drpts = PatientDiagnosticReport._get_diagnostic_report(smart)

        if drpts is None:
            return None

        patientdrpts = []

        for dr in drpts:
            if dr.basedOn is not None:
                patientdrpt = PatientDiagnosticReport.fromFHIRCondition(dr)
                patientdrpts.append(patientdrpt)

        return patientdrpts
