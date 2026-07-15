from datetime import datetime, timezone
import whois

def get_whois_info(domain):
    try:
        data = whois.whois(domain)

        creation_date = data.creation_date
        expiry_date = data.expiration_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if isinstance(expiry_date, list):
            expiry_date = expiry_date[0]

        domain_age = None

        if creation_date:
            if creation_date.tzinfo is not None:
                now = datetime.now(timezone.utc)
            else:
                now = datetime.now()

            domain_age = (now - creation_date).days

        return {
            "registrar": data.registrar if data.registrar else "Unavailable",
            "creation_date": creation_date,
            "expiry_date": expiry_date,
            "country": data.country if data.country else "Unavailable",
            "domain_age": domain_age
        }

    except Exception as e:
        return {
            "registrar": "Unavailable",
            "creation_date": None,
            "expiry_date": None,
            "country": "Unavailable",
            "domain_age": None,
            "error": str(e)
        }