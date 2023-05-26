class CalendarEventModel:
    def __init__(
        self,
        event_id,
        summary,
        description,
        start_time,
        end_time,
        attendees=None,
        location=None,
        reminders=None
    ):
        self.event_id = event_id
        self.summary = summary
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.attendees = attendees or []
        self.location = location
        self.reminders = reminders or {}

    @classmethod
    def from_dict(cls, event_data):
        event_id = event_data.get('id')
        summary = event_data.get('summary')
        description = event_data.get('description')
        start_time = event_data.get('start', {}).get('dateTime')
        end_time = event_data.get('end', {}).get('dateTime')
        attendees = event_data.get('attendees', [])
        location = event_data.get('location')
        reminders = event_data.get('reminders', {}).get('overrides', [])

        parsed_attendees = []
        for attendee in attendees:
            attendee_id = attendee.get('id')
            attendee_email = attendee.get('email')
            attendee_display_name = attendee.get('displayName')
            parsed_attendees.append({
                'id': attendee_id,
                'email': attendee_email,
                'display_name': attendee_display_name
            })

        parsed_reminders = {}
        for reminder in reminders:
            reminder_method = reminder.get('method')
            reminder_minutes = reminder.get('minutes')
            parsed_reminders[reminder_method] = reminder_minutes

        return cls(
            event_id=event_id,
            summary=summary,
            description=description,
            start_time=start_time,
            end_time=end_time,
            attendees=parsed_attendees,
            location=location,
            reminders=parsed_reminders
        )
