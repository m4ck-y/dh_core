# Core Service Static UI

Test UI for `dh_core` endpoints, served at `GET /`.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Tabbed layout with 4 sections. |
| `styles.css` | Retro terminal theme via CSS custom properties. |
| `app.js` | `APIClient` + `CoreUI` class. |

## Layout

```
+--------------------------------------------------+
| TOPBAR: CORE // PEOPLE   PERSON | CONTACT | ...  |
+--------------------------------------------------+
| CONTENT (tab-switched)                            |
|                                                   |
|  PERSON tab:                                      |
|    GET /v1/people/persons/{uuid}                  |
|    POST /v1/people/persons                        |
|    GET /v1/people/persons/check-exists            |
|    PATCH /v1/people/persons/{uuid}/status         |
|                                                   |
|  CONTACT tab: Email and Phone endpoints           |
|  IDENTITY tab: Personal identifiers               |
|  SOCIAL tab: Emergency contacts                   |
+--------------------------------------------------+
| API_REFERENCE: /docs /redoc /openapi.json         |
+--------------------------------------------------+
```

## Sections

| Tab | Entities | Endpoints |
|-----|----------|-----------|
| PERSON | Person | Get, Create, CheckExists, UpdateStatus |
| CONTACT | Email, Phone | Create + List for each |
| IDENTITY | PersonalIdentifier | Create + List |
| SOCIAL | EmergencyContact | Create + List |
