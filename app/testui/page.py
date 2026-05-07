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


def build(root_path: str):
    js = f"{root_path}/static/app.js"

    person_form = f"""<label>EMAIL</label>{_i('p-email','email')}
<label>FIRST NAME</label>{_i('p-fname','first_name')}
<label>LAST NAME</label>{_i('p-lname','last_name')}
<label>PHONE CODE / NUMBER</label>{_i('p-phone-code','+52','+52')} {_i('p-phone-num','5500000000','5500000000')}
<label>BIRTH DATE</label><input type="date" id="p-birth" value="1990-01-01" style="width:100%">
<label>BIRTH COUNTRY</label>{_i('p-birth-country','MX','MX')}
<label>ID TYPE</label><select id="p-id-type" style="width:100%"><option value="NATIONAL_ID">NATIONAL_ID</option><option value="FISCAL_ID">FISCAL_ID</option><option value="SOCIAL_SECURITY_ID">SOCIAL_SECURITY_ID</option></select>
<label>ID VALUE</label>{_i('p-id-value','identifier value')}"""

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

    person = _section("PERSON", "person",
        '<span class="verb get">GET</span><span class="path">/v1/people/{uuid}</span>&nbsp;'
        '<span class="verb post">POST</span><span class="path">/v1/people</span>&nbsp;'
        '<span class="verb patch">PATCH</span><span class="path">/v1/people/{uuid}</span>&nbsp;'
        '<span class="verb delete">DELETE</span><span class="path">/v1/people/{uuid}</span>',
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
        tabs={"person": person, "address": address, "contact": contact, "identity": identity, "social": social, "validation": validation},
        js_module=js, active_tab="person", extra_footer=shared_panel)


def _i(id_, ph, val=""):
    v = f' value="{val}"' if val else ""
    return f'<input type="text" id="{id_}" placeholder="{ph}"{v} style="width:100%">'