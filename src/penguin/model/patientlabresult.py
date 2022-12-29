from datetime import datetime
from dataclasses import dataclass

from fhirclient.models.observation import Observation

bp_component = ['systolic', 'systolicUnit', 'diastolic', 'diastolicUnit']


# https://build.fhir.org/observation-vitalsigns.html
@dataclass
class PatientLabResult:
    name: str
    effdate: datetime
    issdate: datetime
    value: str
    unit: str
    bp: dict.fromkeys(bp_component)

    def toString(self):
        if self.name == 'Blood Pressure':
            return "{0} Date: {1}   Reading:Systolic: {2} {3}   Diastolic: {4} {5}".format(
               self.vitalsign,
               self.issdate,
               self.bp['systolic'],
               self.bp['systolicUnit'],
               self.bp['diastolic'],
               self.bp['diastolicUnit'])
        else:
            return "{0} Date: {1}   Reading:{2} {3}".format(
                self.vitalsign,
                self.issdate,
                self.value,
                self.unit)

    @classmethod
    def fromFHIRObservation(cls, vs: Observation):
        bp: dict.fromkeys(bp_component) = {}
        vitalsign = vs.code.text
        effdate = vs.effectiveDateTime.isostring
        issdate = vs.issued.isostring
        value = vs.valueQuantity.value if vs.valueQuantity is not None else None
        unit = vs.valueQuantity.unit if vs.valueQuantity is not None else None

        if vs.component is not None:
            SystolicValQty = next((oc.valueQuantity for oc in vs.component
                   if oc.code.text == "Systolic blood pressure"), None)
            DiastolicValQty = next((oc.valueQuantity for oc in vs.component
                    if oc.code.text == "Diastolic blood pressure"), None)
            bp['systolic'] = SystolicValQty.value
            bp['systolicUnit'] = SystolicValQty.unit
            bp['diastolic'] = DiastolicValQty.value
            bp['diastolicUnit'] = DiastolicValQty.unit

        return cls(vitalsign=vitalsign,
                   effdate=effdate,
                   issdate=issdate,
                   value=value,
                   unit=unit,
                   bp=bp)

    @staticmethod
    def _get_observation(smart):
        resources = Observation.where(struct={'patient': smart.patient_id,
                                              'category': 'laboratory'}).\
            perform_resources(smart.server)

        resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        return resources_

    @staticmethod
    def get_patient_lab_results(smart):
        labresults = PatientLabResult._get_observation(smart)

        if labresults is None:
            return None

        patientlabresults = []

        for lab in labresults:
            patientlabresult = PatientLabResult.fromFHIRObservation(lab)
            patientlabresults.append(patientlabresult)

        patientlabresults.sort(key=lambda x: (x.vitalsign, x.issdate), reverse=True)
        return patientlabresults
