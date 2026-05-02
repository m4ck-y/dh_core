# dh_core Endpoints Documentation

## Base Path: `/v1/people`
Protocol: **HTTP/REST**

---

### PERSON

#### Get Person
- `GET /persons/{person_uuid}` — Person data by UUID.
- **Success**: `200` / **Error**: `404`

#### Create Person
- `POST /persons` — Create person with email, phone, birth info.
- **Success**: `201`
- **Body**: `{ "email", "first_name", "last_name", "birth_date", "key_birth_country", "phone_code", "phone_number" }`

#### Update Person Status
- `PATCH /persons/{person_uuid}/status` — Change `verification_status`.
- **Body**: `{ "verification_status": "APPROVED" }`

#### Check Person Exists
- `GET /persons/check-exists?email=...&curp=...`
- **Response**: `{ "data": { "exists": true, "person_uuid": "..." } }`

---

### CONTACT (Emails & Phones)

#### Create Email
- `POST /persons/{person_uuid}/emails`
- **Body**: `{ "email": "user@example.com", "type_email": "PERSONAL" }`

#### List Emails
- `GET /persons/{person_uuid}/emails`

#### Create Phone
- `POST /persons/{person_uuid}/phones`
- **Body**: `{ "code": "+52", "number": "5512345678", "type_phone": "MOBILE" }`

#### List Phones
- `GET /persons/{person_uuid}/phones`

---

### IDENTITY (Identifiers)

#### Create Identifier
- `POST /persons/{person_uuid}/identifiers`
- **Body**: `{ "id_identifier_type": "NATIONAL_ID", "identifier_value": "CURP" }`

#### List Identifiers
- `GET /persons/{person_uuid}/identifiers`

---

### SOCIAL (Emergency Contacts)

#### Create Emergency Contact
- `POST /persons/{person_uuid}/emergency-contacts`
- **Body**: `{ "first_name": "...", "last_name": "...", "relationship_type": "OTHER" }`

#### List Emergency Contacts
- `GET /persons/{person_uuid}/emergency-contacts`
