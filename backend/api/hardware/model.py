from backend.shared.hardware_pool import HardwarePool
from flask_mongoengine import MongoEngine
from mongoengine import Document, ReferenceField,ListField
from backend import db

class HwSet(db.Document):
    username = db.StringField(required=True)
    project_id = db.StringField(required=True)
    hw_name = db.StringField(required=True)   
    hw_amount = db.IntField(required=True)
    hardware_from_pool = ReferenceField(HardwarePool)

    def add_hardware(self, amount):
        self.hw_amount += amount
        self.save()
    
    def return_hardware(self, amount):
        if int(amount) > self.hw_amount:
            return False   
        else:  
            self.hw_amount -= int(amount)
            self.save()
            return True
    
    def get_totalamount(self):
        return self.hw_amount 
    
    def get_name(self):
        return self.hw_name   
    
