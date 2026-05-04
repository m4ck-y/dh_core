# dh_core Endpoints Documentation

## Base Path: `/v1/people`
Protocol: **HTTP/REST**

---

### PEOPLE

#### List
- `GET /people` — Paginated list of all persons.
- **Query**: `?page=1&limit=50`
- **Response**: `ApiResponsePaginated[PersonResponseDTO]`

#### Get
- `GET /people/{uuid_person}` — Person data by UUID.
- **Success**: `200` / **Error**: `404`

#### Create
- `POST /people` — Create person with email, phone, birth info.
- **Success**: `201`
- **Body**: `{ "email", "first_name", "last_name", "birth_date", "key_birth_country", "phone_code", "phone_number", "curp?" }`

#### Update
- `PATCH /people/{uuid_person}` — Update mutable fields.
- **Success**: `200` / **Error**: `404`
- **Body**: `{ "first_name?", "last_name?", "second_last_name?", "type_gender?", "verification_status?" }`

#### Update Status
- `PATCH /people/{uuid_person}/status` — Change `verification_status`.
- **Body**: `{ "verification_status": "APPROVED" }`

#### Delete
- `DELETE /people/{uuid_person}` — Soft-delete a person.
- **Success**: `204` / **Error**: `404`

---

### VALIDATION

#### Check Conflicts
- `GET /people/check-exists?email=...&personal_id=...&phone_code=...&phone_number=...`
- **Response**: `{ "data": { "email_already_registered": false, "personal_id_already_registered": false, "phone_already_registered": false } }`
- UUIDs are logged internally — never exposed.

---

### ADDRESS

#### List
- `GET /people/{uuid_person}/address`
- **Response**: `ApiResponsePaginated[AddressResponseDTO]`

#### Create
- `POST /people/{uuid_person}/address`
- **Body**: `{ "postal_code", "key_state", "key_municipality", "address", "type_address?" }`
- **Success**: `201`

#### Update
- `PATCH /people/{uuid_person}/address`
- **Body**: `{ "postal_code?", "key_state?", "key_municipality?", "key_colony?", "address?", "address_complement?", "type_address?" }`
- **Success**: `200` / **Error**: `404`

#### Delete
- `DELETE /people/{uuid_person}/address`
- **Success**: `204` / **Error**: `404`

---

### CONTACT

#### Create Email
- `POST /people/{uuid_person}/emails`
- **Body**: `{ "email": "user@example.com", "type_email": "PERSONAL" }`

#### List Emails
- `GET /people/{uuid_person}/emails`

#### Update Email
- `PATCH /people/{uuid_person}/emails`
- **Body**: `{ "type_email?": "WORK" }`

#### Delete Email
- `DELETE /people/{uuid_person}/emails` → `204`

#### Create Phone
- `POST /people/{uuid_person}/phones`
- **Body**: `{ "code": "+52", "number": "5512345678", "type_phone": "MOBILE" }`

#### List Phones
- `GET /people/{uuid_person}/phones`

#### Update Phone
- `PATCH /people/{uuid_person}/phones`
- **Body**: `{ "code?", "number?", "type_phone?" }`

#### Delete Phone
- `DELETE /people/{uuid_person}/phones` → `204`

---

### IDENTITY

#### Create Identifier
- `POST /people/{uuid_person}/identifiers`
- **Body**: `{ "id_identifier_type": "NATIONAL_ID", "identifier_value": "CURP" }`

#### List Identifiers
- `GET /people/{uuid_person}/identifiers`

#### Update Identifier
- `PATCH /people/{uuid_person}/identifiers`
- **Body**: `{ "id_identifier_type?", "identifier_value?" }`

#### Delete Identifier
- `DELETE /people/{uuid_person}/identifiers` → `204`

---

### SOCIAL

#### Create Emergency Contact
- `POST /people/{uuid_person}/emergency-contacts`
- **Body**: `{ "first_name": "...", "last_name": "...", "relationship_type": "OTHER" }`

#### List Emergency Contacts
- `GET /people/{uuid_person}/emergency-contacts`

#### Update Emergency Contact
- `PATCH /people/{uuid_person}/emergency-contacts`
- **Body**: `{ "first_name?", "last_name?", "phone_number?", "email?", "relationship_type?", "notes?" }`

#### Delete Emergency Contact
- `DELETE /people/{uuid_person}/emergency-contacts` → `204`
