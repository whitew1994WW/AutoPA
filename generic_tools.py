from external_apis import Appointment
from persistant_state import APPOINTMENT_MANAGER
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
    return APPOINTMENT_MANAGER.get_booked_appointments_between(start_date, end_date, appointee_name)

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

