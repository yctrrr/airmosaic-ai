# Geocoding: local sources and selected services

**English** | [中文](geocoding_ZH.md)

This is an acquisition/quality path, not an enabled geocoding API. First distinguish forward address lookup, reverse lookup and administrative point-in-polygon matching. A result from one does not validate the others.

## Service choice and privacy

Prefer an authorized local gazetteer or institutional service when it fits the task. Online geocoding sends address/location information to a third party. The user's explicit authorized online task can define that scope; do not ask again for the same permitted action. Residential, patient, employee or confidential locations must not be submitted without an appropriate permitted route. Keep private queries, returned exact coordinates and caches outside Git.

**Public Nominatim is not a default generic agent geocoder.** Its [current policy](https://operations.osmfoundation.org/policies/nominatim/) requires a deliberate informed developer choice, limits traffic (at most one request per second for the public server, with additional bulk restrictions), requires identification/attribution and caching, forbids personal/confidential submissions, autocomplete and systematic extraction. A generic skill must not silently build it into an address service. Self-hosted/other providers have their own applicable terms; a client library does not override them.

[geopy](https://geopy.readthedocs.io/en/stable/) and [tidygeocoder](https://jessecambon.github.io/tidygeocoder/articles/tidygeocoder.html) expose forward/reverse client methods for multiple providers. Select a provider, endpoint, region/language, rate, retry budget and permitted cache terms before writing its task adapter. Neither library is a universal free backend. No live service is verified by this skill.

## Workflow

1. Preserve the source row key, address provenance/date and intended precision. Normalize spelling/spacing with an audit; do not remove meaningful building or locality information indiscriminately.
2. Resolve against a permitted local gazetteer first where appropriate. Duplicate names require locality context and candidate retention; zero matches remain missing.
3. For an authorized online route, choose provider-specific credentials from the user's protected mechanism, pass only necessary fields and apply current quotas and bounded retries. Never log a request URL containing keys, private query text or raw authentication errors.
4. Retain candidate coordinates, coordinate convention, provider/version, returned precision/type, region agreement and manual-review state. Provider confidence scores are not interchangeable or automatically metre-level errors.
5. Reject or review multiple plausible candidates, unexpected country/region and a city centroid returned for a site-level question. Do not invent a site coordinate from a weak match.
6. Validate required spatial relationships separately using a versioned boundary. Save a fresh external version only after review; no silent promotion or source overwriting.

## Language paths

| Operation | R route | Python route |
|---|---|---|
| Local gazetteer | Explicit keyed join and candidate counts in a prepared table | pandas merge with preserved keys and candidate counts |
| Forward lookup | Provider-specific `tidygeocoder::geocode` / `geo` | Selected geopy provider's `geocode` method |
| Reverse lookup | Provider-specific `reverse_geocode` / `reverse_geo` | Selected provider's `reverse` method |
| Administrative assignment | R containment helper, with known CRS and reviewed boundaries | Python containment helper under the same contract |
| Provider-coordinate conversion | Separately reviewed provider interface | Separately reviewed provider interface |

There is no default provider, hidden API key loader or generic network executable. Any online adapter remains task-specific until tested and registered. [AMap's coordinate interface](https://lbs.amap.com/api/webservice/guide/api/convert) is an example of a separate provider contract, not an ordinary EPSG transform or an implemented service here.

## Minimum records

Use a private task table with source ID, query classification, source/provider version, candidate count, returned precision, coordinate convention, resolution/review status and cache policy. Keep API keys and session state separate. Public summaries may report aggregate match rates and validation methods, with personal query text and sensitive coordinates removed.
