from datetime import date
from dataclasses import dataclass

from fhirclient.server import FHIRPermissionDeniedException
from fhirclient.models.diagnosticreport import DiagnosticReport

# https://hl7.org/fhir/condition.html
# https://patient-browser.smarthealthit.org/#/patient/2

# INCOMPLETE - WORK IN PROGRESS

@dataclass
class PatientDiagnosticReport:
    exception: bool
    clinicalStatus: str
    verificationStatus: str
    severity: str
    condition: str
    onsetStart: date
    onsetEnd: date
    recordedDate: date
    exceptionMessage: str

    @classmethod
    def fromFHIRCondition(cls, dr: DiagnosticReport):
        return None
        status = dr.clinicalStatus.text
        verStatus = dr.verificationStatus.text if dr.verificationStatus is not None else ""
        condition = dr.code.text if dr.code is not None else ""
        recDate = dr.recordedDate.isostring if dr.recordedDate is not None else None
        onsetStart = dr.onsetPeriod.start.isostring if dr.onsetPeriod is not None else None
        onsetEnd = dr.onsetPeriod.end.isostring if dr.onsetPeriod is not None else None
        severity = dr.severity

        return cls(clinicalStatus=status,
                   verificationStatus=verStatus,
                   severity=severity,
                   condition=condition,
                   onsetStart=onsetStart,
                   onsetEnd=onsetEnd,
                   recordedDate=recDate)

    def toString(self):
        return None
        return "Date:{0}  {1} Clinical Status: {2}  Verification Status:{3}".format(
            self.recordedDate,
            self.condition,
            self.clinicalStatus,
            self.verificationStatus)

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
            patientdrpt = PatientDiagnosticReport.fromFHIRCondition(dr)
            patientdrpts.append(patientdrpt)

        return patientdrpts
