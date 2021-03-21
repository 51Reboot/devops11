from rest_framework.throttling import AnonRateThrottle



class CustomAnonRateThrottle(AnonRateThrottle):
    # Throttling
    # key ":1:throttle_anon_127.0.0.1"
    THROTTLE_RATES = {
        'anon': "3/m"
    }