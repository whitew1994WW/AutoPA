# These are dummy functions that simulate the behavior of external APIs
import datetime
from typing import Optional


class Appointment:
    def __init__(self, time: datetime.datetime, length: int, appointment_name: Optional[str] = None, appointee_name: Optional[str] = None):
        self.time = time
        self.length = length
        self.appointment_name = appointment_name
        self.appointee_name = appointee_name

    def __str__(self):
        return f"{self.time.strftime('%Y-%m-%d %H:%M')} - {self.appointment_name} - {self.appointee_name} - {self.length} mins"

class AppointmentManager:
    booked_appointments = []
    def get_next_available_time(self, length=30, num_slots=5):
        """Returns the next available time rounded to the nearest 30 minutes that is between 9 and 5"""
        # Round the current time up to the nearest 30 minutes
        current_time = datetime.datetime.now()
        current_time += datetime.timedelta(minutes=(30 - current_time.minute % 30))
        available_times = []
        while len(available_times) < num_slots:
            if self.check_availability(current_time, length):
                available_times.append(current_time)
            current_time += datetime.timedelta(minutes=30)
        return available_times

    def get_available_appointments_between(self, start: datetime.datetime, end: datetime.datetime, length=30):
        """Returns a list of available appointments between the start and end times"""
        if start == end:
            end += datetime.timedelta(days=1)
        available_appointments = []
        current_time = start
        while current_time < end:
            if self.check_availability(current_time, length):
                available_appointments.append(current_time)
            current_time += datetime.timedelta(minutes=30)
        return available_appointments


    def check_availability(self, time: datetime.datetime, length=30):
        """"Always available 9 - 5 Monday to friday"""
        available = False
        if 9 <= time.hour < 17:
            available = True
        return available

    def book_appointment(self, time: datetime.datetime, length=30, appointment_name=None, appointee_name=None):
        # Check if the appointment is available
        if not self.check_availability(time, length):
            # Check if the appointment is already booked for this appointee
            for appointment in self.booked_appointments:
                if appointment.time == time and appointment.appointee_name == appointee_name:
                    return f"Appointment already booked for {time}"
            else:
                return f"Appointment not available at {time}"
        self.booked_appointments.append(Appointment(time, length, appointment_name, appointee_name))
        return f"Appointment booked for {time} for {length} minutes"

    def get_booked_appointments_between(self, start: datetime.datetime, end: datetime.datetime, appointee_name=None):
        """Get all appointments between start and end"""
        if start == end:
            end += datetime.timedelta(days=1)
        appointments = []
        for appointment in self.booked_appointments:
            if start <= appointment.time <= end and (appointee_name is None or appointment.appointee_name == appointee_name):
                appointments.append(appointment)
        return appointments

    def cancel_appointment(self, time: datetime.datetime, appointee_name=None):
        """Cancel the appointment at the given time"""
        for appointment in self.booked_appointments:
            if appointment.time == time:
                self.booked_appointments.remove(appointment)
                return f"Appointment at {time} cancelled"
        return f"No appointment found at {time}"
    
class Contact:
    name: str
    phone_number: str
    email: str
    notes: str

    def __init__(self, name: str, phone_number: str=None, email: str=None, notes: str=None):
        self.name = name
        self.phone_number = phone_number
        self.email = email
        self.notes = notes

    def __str__(self) -> str:
        return f"Name: {self.name} - Number: {self.phone_number} - Email: {self.email} - Notes: {self.notes}"

class ContactManager:
    def __init__(self):
        self.contacts = []

    def add_or_update_contact(self, name: str, phone_number: str=None, email: str=None, notes: str=None):
        # Get any current contact details associated with the name, number, or email and then merge the new details
        for contact in self.contacts:
            if contact.name == name or contact.phone_number == phone_number or contact.email == email:
                if phone_number:
                    contact.phone_number = phone_number
                if email:
                    contact.email = email
                if notes:
                    contact.notes = notes
                contact.name = name
                return "Contact updated"
        self.contacts.append(Contact(name, phone_number, email, notes))


    def get_contact(self, name: str=None, phone_number: str=None, email: str=None):
        if not (name or phone_number or email):
            return "No contact information provided"
        for contact in self.contacts:
            if name and contact.name == name:
                return contact
            if phone_number and contact.phone_number == phone_number:
                return contact
            if email and contact.email == email:
                return contact
        return "Contact not found"
    
    def is_contact_in_list(self, name: str=None, phone_number: str=None, email: str=None):
        if not (name or phone_number or email):
            return "No contact information provided"
        for contact in self.contacts:
            if name and contact.name == name:
                return True
            if phone_number and contact.phone_number == phone_number:
                return True
            if email and contact.email == email:
                return True
        return False

    def delete_contact(self, name=None, phone_number=None, email=None):
        if not (name or phone_number or email):
            return "No contact information provided"
        for contact in self.contacts:
            if name and contact.name == name:
                del self.contacts[name]
            if phone_number and contact.phone_number == phone_number:
                del self.contacts[name]
            if email and contact.email == email:
                del self.contacts[name]
