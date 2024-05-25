# These are dummy functions that simulate the behavior of external APIs
import datetime
import random
from typing import Optional

booked_appointments = []

class Appointment:
    def __init__(self, time: datetime.datetime, length: int, appointment_name: Optional[str] = None, appointee_name: Optional[str] = None):
        self.time = time
        self.length = length
        self.appointment_name = appointment_name
        self.appointee_name = appointee_name


def get_next_available_time(length=30, num_slots=5):
    """Returns the next available time rounded to the nearest 30 minutes that is between 9 and 5"""
    # Round the current time up to the nearest 30 minutes
    current_time = datetime.datetime.now()
    current_time += datetime.timedelta(minutes=(30 - current_time.minute % 30))
    available_times = []
    while len(available_times) < num_slots:
        if check_availability(current_time, length):
            available_times.append(current_time)
        current_time += datetime.timedelta(minutes=30)
    return available_times

def get_available_appointments_between(start: datetime.datetime, end: datetime.datetime, length=30):
    """Returns a list of available appointments between the start and end times"""
    if start == end:
        end += datetime.timedelta(days=1)
    available_appointments = []
    current_time = start
    while current_time < end:
        if check_availability(current_time, length):
            available_appointments.append(current_time)
        current_time += datetime.timedelta(minutes=30)
    return available_appointments


def check_availability(time: datetime.datetime, length=30):
    """"Always available 9 - 5 Monday to friday"""
    available = False
    if 9 <= time.hour < 17:
        available = True
    return available

def book_appointment(time: datetime.datetime, length=30, appointment_name=None, appointee_name=None):
    # Check if the appointment is available
    if not check_availability(time, length):
        # Check if the appointment is already booked for this appointee
        for appointment in booked_appointments:
            if appointment.time == time and appointment.appointee_name == appointee_name:
                return f"Appointment already booked for {time}"
        else:
            return f"Appointment not available at {time}"
    booked_appointments.append(Appointment(time, length, appointment_name, appointee_name))
    return f"Appointment booked for {time} for {length} minutes"

def get_appointments(start: datetime.datetime, end: datetime.datetime, appointee_name=None):
    """Get all appointments between start and end"""
    appointments = []
    for appointment in booked_appointments:
        if start <= appointment.time <= end and (appointee_name is None or appointment.appointee_name == appointee_name):
            appointments.append(appointment)
    return appointments

def cancel_appointment(time: datetime.datetime, appointee_name=None):
    """Cancel the appointment at the given time"""
    for appointment in booked_appointments:
        if appointment.time == time:
            booked_appointments.remove(appointment)
            return f"Appointment at {time} cancelled"
    return f"No appointment found at {time}"