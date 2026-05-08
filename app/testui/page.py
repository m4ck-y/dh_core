from dh_shared.testui.templates.crud import render_crud_page
from dh_shared.testui.components import render_button, render_input, render_json_pre, render_panel_actions


def _section(title, tab, ep_html, add_html, *, list_all=True):
    list_btn = render_button("LIST ALL", "GET", f"{tab}-list-btn") if list_all else ""
    return f"""<div class="panel">
<h3>{title}
{list_btn}
{render_button("ADD", "POST", f"{tab}-add-btn")}
{render_button("EDIT", "PATCH", f"{tab}-edit-btn")}
{render_button("DELETE", "DELETE", f"{tab}-delete-btn")}
</h3>

{render_input(f"{tab}-fetch-uuid", "uuid person", size=130, input_id=f"{tab}-fetch-uuid")}
{render_button("FETCH", "GET", f"{tab}-fetch-btn")}
{render_json_pre(f"out-{tab}", "...")}
<div class="endpoint-tag" style="margin-top:6px;color:var(--color-dim)">{ep_html}</div>
</div>"""


def _panel_wrap(tab, add_html, entity_label="entity"):
    return f"""<div id="{tab}-panel-wrap" style="display:none">
<div id="{tab}-mode" style="display:none;margin-bottom:8px;color:var(--color-amber);font-size:12px"></div>
<div id="{tab}-edit-section" style="display:none;margin-bottom:8px">
{render_input(f"{tab}-edit-uuid", f"uuid {entity_label}", "UUID", input_id=f"{tab}-edit-uuid")}
{render_button("SEARCH", "GET", f"{tab}-edit-fetch-btn")}
</div>
<div id="{tab}-panel-body">{add_html}</div>
{render_panel_actions(f"{tab}-cancel", f"{tab}-save")}
<div id="{tab}-endpoint-footer" class="endpoint-tag" style="margin-top:12px;padding-top:8px;border-top:1px solid var(--color-border,#333)"></div>
</div>"""


def _sub_label(text):
    """Inline section label inside a modal form for 1:1 sub-resources."""
    return f'<div style="color:var(--color-cyan);font-size:11px;margin:10px 0 4px;letter-spacing:1px">&rsaquo; {text}</div>'


def build(root_path: str):
    js = f"{root_path}/static/app.js"

    # ── Person form — includes all 1:1 sub-resource fields ───────
    # Tabs are only for 1:N. 1:1 entities are grouped here (ADR 025).
    person_form = f"""{_sub_label("PERSON")}
<label>FIRST NAME</label>{_i('p-fname','first_name')}
<label>LAST NAME</label>{_i('p-lname','last_name')}
<label>SECOND LAST NAME</label>{_i('p-slname','optional')}
<label>GENDER</label><select id="p-gender" style="width:100%"><option value="">— not specified —</option><option value="MASCULINO">MASCULINO</option><option value="FEMENINO">FEMENINO</option><option value="TRANSGENERO">TRANSGENERO</option><option value="TRANSEXUAL">TRANSEXUAL</option><option value="TRAVESTI">TRAVESTI</option><option value="INTERSEXUAL">INTERSEXUAL</option><option value="OTRO">OTRO</option></select>
<hr>
{_sub_label("BIRTH — /v1/people/{'{uuid}'}/birth")}
<label>BIRTH DATE</label><input type="date" id="p-birth" value="1990-01-01" data-init="1990-01-01" style="width:100%">
<label>BIRTH COUNTRY</label>{_i('p-birth-country','MX','MX')}
<label>BIRTH STATE</label>{_i('p-birth-state','state code')}
<hr>
{_sub_label("LEGAL INFO — optional — /v1/people/{'{uuid}'}/legal-info")}
<label>NATIONALITY</label>{_i('p-nationality','MX')}
<label>CIVIL STATUS</label><select id="p-civil" style="width:100%"><option value="">—</option><option value="SINGLE">SINGLE</option><option value="MARRIED">MARRIED</option><option value="COMMON_LAW">COMMON_LAW</option><option value="SEPARATED">SEPARATED</option><option value="DIVORCED">DIVORCED</option><option value="WIDOWED">WIDOWED</option><option value="PREFERS_NOT_TO_SAY">PREFERS_NOT_TO_SAY</option></select>
<label>ID SEX (official doc)</label><select id="p-id-sex" style="width:100%"><option value="">—</option><option value="M">M</option><option value="F">F</option></select>
<hr>
{_sub_label("PROFILE — optional — /v1/people/{'{uuid}'}/profile")}
<label>KNOWN AS</label>{_i('p-known-as','alias or nickname')}
<label>OCCUPATION</label><select id="p-occupation" style="width:100%"><option value="">—</option><option value="EMPLOYED">EMPLOYED</option><option value="SELF_EMPLOYED">SELF_EMPLOYED</option><option value="FREELANCE">FREELANCE</option><option value="HOMEMAKER">HOMEMAKER</option><option value="UNEMPLOYED">UNEMPLOYED</option><option value="RETIRED">RETIRED</option><option value="OTHER">OTHER</option><option value="PREFERS_NOT_TO_SAY">PREFERS_NOT_TO_SAY</option></select>
<label>EDUCATION</label><select id="p-education" style="width:100%"><option value="">—</option><option value="NO_STUDIES">NO_STUDIES</option><option value="PRIMARY">PRIMARY</option><option value="SECONDARY">SECONDARY</option><option value="HIGH_SCHOOL">HIGH_SCHOOL</option><option value="UNIVERSITY">UNIVERSITY</option><option value="POSTGRADUATE">POSTGRADUATE</option><option value="PREFERS_NOT_TO_SAY">PREFERS_NOT_TO_SAY</option></select>
<hr>
{_sub_label("SOCIOCULTURAL — optional — /v1/people/{'{uuid}'}/sociocultural-identity")}
<label>INDIGENOUS</label><select id="p-indigenous" style="width:100%"><option value="">—</option><option value="true">YES</option><option value="false">NO</option></select>
<label>MIGRANT</label><select id="p-migrant" style="width:100%"><option value="">—</option><option value="true">YES</option><option value="false">NO</option></select>
<label>COUNTRY ORIGIN</label>{_i('p-country-origin','catalog key')}
<label>RELIGION</label>{_i('p-religion','catalog key')}"""

    # ── 1:N forms ─────────────────────────────────────────────────
    address_form = f"""<label>STREET</label>{_i('a-street','street address')}
<label>POSTAL CODE</label>{_i('a-zip','postal_code')}
<label>STATE</label>{_i('a-state','CMX','CMX')}
<label>MUNICIPALITY</label>{_i('a-mun','016','016')}"""

    email_form = f"""<label>EMAIL</label>{_i('em-addr','email address')}
<label>TYPE</label><select id="em-type" style="width:100%"><option value="PERSONAL">PERSONAL</option><option value="WORK">WORK</option><option value="OTHER">OTHER</option></select>"""

    phone_form = f"""<label>CODE</label>{_i('ph-code','+52','+52')}
<label>NUMBER</label>{_i('ph-num','5500000000')}
<label>TYPE</label><select id="ph-type" style="width:100%"><option value="MOBILE">MOBILE</option><option value="HOME">HOME</option><option value="WORK">WORK</option></select>"""

    identity_form = f"""<label>TYPE</label><select id="i-type" style="width:100%"><option value="NATIONAL_ID">NATIONAL_ID</option><option value="FISCAL_ID">FISCAL_ID</option><option value="SOCIAL_SECURITY_ID">SOCIAL_SECURITY_ID</option></select>
<label>VALUE</label>{_i('i-val','identifier value')}"""

    social_form = f"""<label>FIRST NAME</label>{_i('s-fname','first_name')}
<label>LAST NAME</label>{_i('s-lname','last_name')}
<label>PHONE</label>{_i('s-phone','phone')}
<label>EMAIL</label>{_i('s-email','email')}
<label>RELATIONSHIP</label><select id="s-rel" style="width:100%"><option value="SPOUSE">SPOUSE</option><option value="PARENT">PARENT</option><option value="SIBLING">SIBLING</option><option value="CHILD">CHILD</option><option value="FRIEND">FRIEND</option><option value="CAREGIVER">CAREGIVER</option><option value="OTHER">OTHER</option></select>"""

    # ── Sections ──────────────────────────────────────────────────
    person = _section("PERSON", "person",
        '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}</span>&nbsp;'
        '<span class="verb post">POST</span><span class="path">/v1/people</span>&nbsp;'
        '<span class="verb patch">PATCH</span><span class="path">/v1/people/{uuid_person}</span>&nbsp;'
        '<span class="verb delete">DELETE</span><span class="path">/v1/people/{uuid_person}</span>',
        person_form)

    address = _section("ADDRESS", "address",
        '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}/addresses</span>&nbsp;'
        '<span class="verb post">POST</span><span class="path">/v1/people/{uuid_person}/addresses</span>&nbsp;'
        '<span class="verb patch">PATCH</span><span class="path">/v1/people/addresses/{uuid_address}</span>&nbsp;'
        '<span class="verb delete">DELETE</span><span class="path">/v1/people/addresses/{uuid_address}</span>',
        address_form, list_all=False)

    contact = (
        _section("EMAILS", "email",
            '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}/emails</span>&nbsp;'
            '<span class="verb post">POST</span><span class="path">/v1/people/{uuid_person}/emails</span>&nbsp;'
            '<span class="verb patch">PATCH</span><span class="path">/v1/people/emails/{uuid_email}</span>&nbsp;'
            '<span class="verb delete">DELETE</span><span class="path">/v1/people/emails/{uuid_email}</span>',
            email_form, list_all=False)
        + "\n" +
        _section("PHONES", "phone",
            '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}/phones</span>&nbsp;'
            '<span class="verb post">POST</span><span class="path">/v1/people/{uuid_person}/phones</span>&nbsp;'
            '<span class="verb patch">PATCH</span><span class="path">/v1/people/phones/{uuid_phone}</span>&nbsp;'
            '<span class="verb delete">DELETE</span><span class="path">/v1/people/phones/{uuid_phone}</span>',
            phone_form, list_all=False)
    )

    identity = _section("IDENTITY", "identity",
        '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}/identifiers</span>&nbsp;'
        '<span class="verb post">POST</span><span class="path">/v1/people/{uuid_person}/identifiers</span>&nbsp;'
        '<span class="verb patch">PATCH</span><span class="path">/v1/people/identifiers/{uuid_identifier}</span>&nbsp;'
        '<span class="verb delete">DELETE</span><span class="path">/v1/people/identifiers/{uuid_identifier}</span>',
        identity_form, list_all=False)

    social = _section("SOCIAL", "social",
        '<span class="verb get">GET</span><span class="path">/v1/people/{uuid_person}/emergency-contacts</span>&nbsp;'
        '<span class="verb post">POST</span><span class="path">/v1/people/{uuid_person}/emergency-contacts</span>&nbsp;'
        '<span class="verb patch">PATCH</span><span class="path">/v1/people/emergency-contacts/{uuid_emergency}</span>&nbsp;'
        '<span class="verb delete">DELETE</span><span class="path">/v1/people/emergency-contacts/{uuid_emergency}</span>',
        social_form, list_all=False)

    validation = f"""<div class="panel">
<h3>VALIDATION</h3>
{render_input("check-email", "email", "EMAIL", input_id="check-email")}
{render_input("check-pid", "personal_id", "IDENTIFIER", input_id="check-pid")}
{render_button("CHECK", "GET", "check-btn")}
<div class="endpoint-tag" style="margin-top:4px;color:var(--color-dim)">
<span class="verb get">GET</span><span class="path">/v1/people/check-exists?email=&amp;personal_id=</span>
</div>
{render_json_pre("out-validation", "...")}
</div>"""

    shared_panel = f"""<div class="overlay" id="overlay"></div>
<div class="side-panel" id="side-panel">
<button class="close-btn" id="panel-close">[X]</button>
<h2 id="panel-title">MANAGE</h2>
{_panel_wrap("person", person_form, "person")}
{_panel_wrap("address", address_form, "address")}
{_panel_wrap("email", email_form, "email")}
{_panel_wrap("phone", phone_form, "phone")}
{_panel_wrap("identity", identity_form, "identifier")}
{_panel_wrap("social", social_form, "emergency contact")}
</div>"""

    return render_crud_page(root_path=root_path, title="CORE // PEOPLE",
        tabs={"person": person, "address": address, "contact": contact,
              "identity": identity, "social": social, "validation": validation},
        js_module=js, active_tab="person", extra_footer=shared_panel)


def _i(id_, ph, val=""):
    v = f' value="{val}"' if val else ""
    return f'<input type="text" id="{id_}" placeholder="{ph}"{v} style="width:100%">'
