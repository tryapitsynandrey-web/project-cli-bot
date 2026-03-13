from datetime import date


def build_contact_payload(name="Alice Example", phone_numbers=None, **kwargs):
    if phone_numbers is None:
        phone_numbers = ["+353830000001"]

    payload = {
        "name": name,
        "phone_numbers": phone_numbers,
    }
    payload.update(kwargs)
    return payload


def build_note_payload(content="Short note", tags=None):
    return {"content": content, "tags": tags or []}


def today_str():
    return date.today().isoformat()
