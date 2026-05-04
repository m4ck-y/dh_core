# Core Service Static UI

Test UI for `dh_core` endpoints, served at `GET /`.

## Files

| File | Purpose |
|------|---------|
| `index.html` | Tabbed layout with 6 sections. |
| `styles.css` | Retro terminal theme via CSS custom properties. |
| `app.js` | `APIClient` + `CoreUI` class. |

## Layout

```
+--------------------------------------------------------------------+
| TOPBAR: CORE // PEOPLE   PERSON | ADDRESS | CONTACT | IDENTITY | ...  |
+--------------------------------------------------------------------+
| CONTENT (tab-switched)                                              |
|                                                                     |
|  PERSON tab:                                                        |
|    GET  /v1/people?page=1&limit=50                                   |
|    GET  /v1/people/{uuid}                                           |
|    POST /v1/people                                                  |
|    PATCH /v1/people/{uuid}                                          |
|    PATCH /v1/people/{uuid}/status                                   |
|    DELETE /v1/people/{uuid}                                         |
|                                                                     |
|  ADDRESS tab: Address endpoints                                     |
|  CONTACT tab: Email and Phone endpoints                             |
|  IDENTITY tab: Personal identifiers                                 |
|  SOCIAL tab: Emergency contacts                                     |
|  VALIDATION tab: Check-exists                                       |
+--------------------------------------------------------------------+
| API_REFERENCE: /docs /redoc /openapi.json                           |
+--------------------------------------------------------------------+
```

## Sections

| Tab | Entities | Endpoints |
|-----|----------|-----------|
| PERSON | Person | List, Get, Create, Update, UpdateStatus, Delete |
| ADDRESS | Address | List, Create, Update, Delete |
| CONTACT | Email, Phone | Create, List, Update, Delete for each |
| IDENTITY | PersonalIdentifier | Create, List, Update, Delete |
| SOCIAL | EmergencyContact | Create, List, Update, Delete |
| VALIDATION | Check Exists | Check conflicts |
