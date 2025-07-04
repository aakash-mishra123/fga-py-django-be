from rolepermissions.roles import AbstractUserRole
from rolepermissions.checkers import has_permission


class Doctor(AbstractUserRole):
    available_permissions = {
        'create_medical_record': True,
    }

class Nurse(AbstractUserRole):
    available_permissions = {
        'edit_patient_file': True,
    }