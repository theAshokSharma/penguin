from datetime import datetime
from dataclasses import dataclass

from fhirclient.models.observation import Observation

bp_component = ['systolic', 'systolicUnit', 'diastolic', 'diastolicUnit']


# http://hl7.org/fhir/vitalsigns.html
@dataclass
class PatientObservation:
    name: str
    effdate: datetime
    issdate: datetime
    value: str
    unit: str
    bp: dict.fromkeys(bp_component)

    def toString(self):
        if self.name == 'Blood Pressure':
            # return "{0} Date: {1}   Reading:Systolic: {2} {3},   Diastolic: {4} {5}".format(
            #    self.name,
            #    self.issdate,
            #    self.bp['systolic'],
            #    self.bp['systolicUnit'],
            #    self.bp['diastolic'],
            #    self.bp['diastolicUnit'])
            return "{0} Date: {1}   Reading: {2}/{3} {4}".format(
               self.name,
               self.issdate,
               self.bp['systolic'],
               self.bp['diastolic'],
               self.bp['diastolicUnit'])          
        else:
            return "{0} Date: {1}   Reading:{2} {3}".format(
               self.name,
               self.issdate,
               self.value,
               self.unit)

    @classmethod
    def fromFHIRObservation(cls, vs: Observation):
        bp: dict.fromkeys(bp_component) = {}
        name = vs.code.text if vs.code is not None else ""
        effdate = vs.effectiveDateTime.isostring if vs.effectiveInstant is not None else ""
        issdate = vs.issued.isostring if vs.issued is not None else ""
        value = None
        unit = None
        if vs.valueCodeableConcept is not None:
            value = vs.valueCodeableConcept.text
        elif vs.valueQuantity is not None:
            value = vs.valueQuantity.value
            unit = vs.valueQuantity.unit

        if vs.component is not None:
            SystolicValQty = next((oc.valueQuantity for oc in vs.component
                   if oc.code.text == "Systolic blood pressure"), None)
            DiastolicValQty = next((oc.valueQuantity for oc in vs.component
                    if oc.code.text == "Diastolic blood pressure"), None)
            bp['systolic'] = SystolicValQty.value if SystolicValQty is not None else None
            bp['systolicUnit'] = SystolicValQty.unit if SystolicValQty is not None else None
            bp['diastolic'] = DiastolicValQty.value if DiastolicValQty is not None else None
            bp['diastolicUnit'] = DiastolicValQty.unit if DiastolicValQty is not None else None

        return cls(name=name,
                   effdate=effdate,
                   issdate=issdate,
                   value=value,
                   unit=unit,
                   bp=bp)

    @staticmethod
    def _get_observation(smart, cat: str):

        try:
            resources = Observation.where(struct={'patient': smart.patient_id,
                                                'category': cat,
                                                'status': 'final'}).\
                perform_resources(smart.server)

            resources_ = [src for src in resources if src.resource_type != 'OperationOutcome']
        except Exception as e:
            resources_ = None

        if resources_ is None:
            return None

        patientobs = []

        for obs in resources_:
            patobs = PatientObservation.fromFHIRObservation(obs)
            patientobs.append(patobs)

        patientobs.sort(key=lambda x: (x.name, x.issdate), reverse=True)

        return patientobs

    @staticmethod
    def get_patient_vital_signs(smart):
        obs_all = PatientObservation._get_observation(smart, 'vital-signs')
        return obs_all

    @staticmethod
    def get_patient_lab_results(smart):
        obs_all = PatientObservation._get_observation(smart, 'laboratory')
        return obs_all

    @staticmethod
    def get_patient_social_history(smart):
        obs_all = PatientObservation._get_observation(smart, 'social-history')
        return obs_all
