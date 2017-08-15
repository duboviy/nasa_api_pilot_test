""" NASA API related constants (URL paths and keys). """

API_KEY = 'cVXCwImHNJ2mCFkIirKZk4e6AruCMg6ldgw0yOIl'  # change to yours, if you won't it will use mine
# DEMO API key can be used for initially exploring APIs prior to signing up, but it has much lower rate limits
DEMO_KEY = "DEMO_KEY"
API_KEY = API_KEY or DEMO_KEY

MAIN_URL = 'https://api.nasa.gov/'
MANIFESTS_URL = '/mars-photos/api/v1/manifests/{rover}'
ROVER_PHOTOS_URL = '/mars-photos/api/v1/rovers/{rover}/photos'

RATIO = 1.02749125170  # ratio of Earth days to SOLs
