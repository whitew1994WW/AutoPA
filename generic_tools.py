from external_apis import Appointment
from persistant_state import APPOINTMENT_MANAGER, CONTACT_MANAGER
from langchain_core.tools import tool
import datetime
from typing import List, Optional

@tool
def get_potential_appointments(start_month: int, start_day: int, start_year: int, end_month: int, end_day: int, end_year: int, length: int = 30):
    """Get the available appointment times between two dates and with the length of the appointment.
    Args:
        start_month: An integer representing the start month
        start_day: An integer representing the start day
        start_year: An integer representing the start year
        end_month: An integer representing the end month
        end_day: An integer representing the end day
        end_year: An integer representing the end year
        length: An integer representing the length of the appointment in minutes
    Returns:
        A list of datetime strings in the format "YYYY-MM-DD HH:MM" representing the available appointments
    """
    next_available_times = APPOINTMENT_MANAGER.get_available_appointments_between(datetime.datetime(start_year, start_month, start_day), datetime.datetime(end_year, end_month, end_day), length)
    return [time.strftime("%Y-%m-%d %H:%M") for time in next_available_times]

@tool
def get_current_appointments(month: int, day: int, year: int,appointee_name: Optional[str] = None) -> List[Appointment]:
    """Get the boss appointments for a specific day.
    Args:
        month: An integer representing the month
        day: An integer representing the day
        year: An integer representing the year
        appointee_name: An optional string representing the name of the person who's appointments to get
    Returns:
        A list of of all the appointments between the start and end dates
    """
    start_date = datetime.datetime(year, month, day)
    end_date = start_date + datetime.timedelta(days=1)
    return [str(appt) for appt in APPOINTMENT_MANAGER.get_booked_appointments_between(start_date, end_date, appointee_name)]

@tool
def book_appointment(day: int, month: int, year: int, hour: int, minutes: int, appointment_name: str, appointee_name: str, length: int = 30):
    """Book an appointment at a specific time and length.
    Args:
        day: An integer representing the day
        month: An integer representing the month
        year: An integer representing the year
        hour: An integer representing the hour (0-24)
        minutes: An integer representing the minutes
        appointment_name: A string representing the name of the appointment
        appointee_name: A string representing the name of the person the appointment is for
        length: An integer representing the length of the appointment in minutes
    Returns:
        A string indicating the appointment was booked
    """
    return APPOINTMENT_MANAGER.book_appointment(datetime.datetime(year, month, day, hour, minutes), length, appointment_name, appointee_name)

@tool
def cancel_appointment(appointment_time: str):
    """Cancel an appointment at a specific time.
    Args:
        appointment_time: A string representing the time of the appointment in the format "YYYY-MM-DD HH:MM"
    Returns:
        A string indicating the appointment was cancelled
    """
    return APPOINTMENT_MANAGER.cancel_appointment(datetime.datetime.strptime(appointment_time, "%Y-%m-%d %H:%M"))

@tool
def add_or_update_contact(name: str, number: Optional[str] = None, email: Optional[str] = None, notes: Optional[str] = None):
    """Add or update a contact to the list of known contacts.
    Args:
        name: A string representing the name of the contact
        number: An optional string representing the phone number of the contact
        email: An optional string representing the email of the contact
        notes: An optional string representing any notes about the contact
    Returns:
        A string indicating the contact was added
    """
    return CONTACT_MANAGER.add_or_update_contact(name, number, email, notes)

@tool
def get_contact(name: Optional[str] = None, number: Optional[str] = None, email: Optional[str] = None):
    """Get a contact from the list of known contacts.
    Args:
        name: An optional string representing the name of the contact
        number: An optional string representing the phone number of the contact
        email: An optional string representing the email of the contact
    Returns:
        A string representing the contact information
    """
    return CONTACT_MANAGER.get_contact(name, number, email)

@tool
def delete_contact(name: str):
    """Delete a contact from the list of known contacts.
    Args:
        name: A string representing the name of the contact
    Returns:
        A string indicating the contact was deleted
    """
    return CONTACT_MANAGER.delete_contact(name)