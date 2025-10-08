import {Component, useState} from "@odoo/owl";

class RBookingForm extends Component {
    static template = "web_resource_booking.RBookingForm";

    setup() {
        this.state = useState({
            type_id: "",
            user_id: "",
            users: [],
            loading: false,
            name: "",
            email: "",
            questions: [],
            formError: "",
        });
        this.csrf = this.props.csrf;
        this.usersEndpoint = this.props.usersEndpoint;
        this.startUrl = this.props.startUrl || "/rbooking/start";
        this.questionsEndpoint = this.props.questionsEndpoint || "/rbooking/questions";
        // Lightweight logger to avoid runtime errors if referenced in handlers
        this._log = (...args) => {
            try {
                console.debug("[web_resource_booking][Form]", ...args);
            } catch {
                /* Ignore */
            }
        };
        // Preselect type from props if provided, and fetch dependent data
        if (this.props.preselectedTypeId) {
            this.state.type_id = String(this.props.preselectedTypeId);
            // Fire and forget; state updates will re-render when data arrives
            this.onTypeChange();
        }
    }

    get selectedType() {
        const id = this.state.type_id;
        return (this.props.types || []).find((t) => String(t.id) === String(id));
    }

    resetType() {
        this._log("resetType");
        this.state.type_id = "";
        this.state.user_id = "";
        this.state.users = [];
        this.state.questions = [];
        this.state.name = "";
        this.state.email = "";
    }

    get selectedUser() {
        const uid = this.state.user_id;
        const list = this.state.users || [];
        return list.find((u) => String(u.id) === String(uid));
    }

    resetUser() {
        this._log("resetUser");
        this.state.user_id = "";
    }

    canSubmit() {
        return Boolean(
            this.state.type_id &&
                this.state.user_id &&
                this.state.name &&
                this.state.email
        );
    }

    async onTypeChange() {
        this.state.user_id = "";
        this.state.users = [];
        this.state.questions = [];
        if (!this.state.type_id) return;
        this.state.loading = true;
        try {
            const urlUsers = `${this.usersEndpoint}?type_id=${encodeURIComponent(this.state.type_id)}`;
            const urlQs = `${this.questionsEndpoint}?type_id=${encodeURIComponent(this.state.type_id)}`;
            const [respUsers, respQs] = await Promise.all([
                fetch(urlUsers, {headers: {Accept: "application/json"}}),
                fetch(urlQs, {headers: {Accept: "application/json"}}),
            ]);
            const dataUsers = await respUsers.json();
            const dataQs = await respQs.json();
            this.state.users = Array.isArray(dataUsers.users) ? dataUsers.users : [];
            this.state.questions = Array.isArray(dataQs.questions)
                ? dataQs.questions
                : [];
        } catch {
            this.state.users = [];
            this.state.questions = [];
        } finally {
            this.state.loading = false;
        }
    }

    onSubmit() {
        // Client-side validation
        const root = this.el || document;
        this._clearInvalid(root);
        const errors = this._validateBasics(root).concat(this._validateQuestions(root));
        if (errors.length) {
            this.state.formError = errors.includes("invalid_email")
                ? "Please enter a valid email address."
                : "Please complete required fields.";
            // Focus first invalid if present
            try {
                const firstInvalid = root.querySelector(".is-invalid");
                if (firstInvalid)
                    firstInvalid.scrollIntoView({behavior: "smooth", block: "center"});
                if (firstInvalid && firstInvalid.focus) firstInvalid.focus();
            } catch {}
            return;
        }
        this.state.formError = "";
        if (!this.canSubmit()) return;
        const form = document.createElement("form");
        form.method = "POST";
        form.action = this.startUrl;
        const fields = {
            csrf_token: this.csrf,
            type_id: this.state.type_id,
            user_id: this.state.user_id,
            name: this.state.name,
            email: this.state.email,
        };
        for (const [k, v] of Object.entries(fields)) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = k;
            input.value = v;
            form.appendChild(input);
        }
        // Serialize dynamic question answers from current form DOM
        try {
            // Component root element
            const root = this.el || document;
            for (const q of this.state.questions) {
                const key = `qa_${q.id}`;
                let val = "";
                if (q.field_type === "boolean") {
                    const el = root.querySelector(`input[name="${key}"]:checked`);
                    val = el ? el.value : "";
                } else if (q.field_type === "select") {
                    const el = root.querySelector(`#${key}`);
                    val = el ? el.value : "";
                } else {
                    const el = root.querySelector(`#${key}`);
                    val = el ? el.value : "";
                }
                if (val !== "") {
                    const input = document.createElement("input");
                    input.type = "hidden";
                    input.name = key;
                    input.value = val;
                    form.appendChild(input);
                }
            }
        } catch {
            // No-op: if we can't serialize questions, backend will ignore
        }
        document.body.appendChild(form);
        form.submit();
    }

    _clearInvalid(root) {
        try {
            root.querySelectorAll(".is-invalid").forEach((el) => {
                el.classList.remove("is-invalid");
                el.removeAttribute("aria-invalid");
            });
        } catch {}
    }

    _markInvalid(el) {
        if (!el) return;
        try {
            el.classList.add("is-invalid");
            el.setAttribute("aria-invalid", "true");
        } catch {}
    }

    _validateBasics(root) {
        const errors = [];
        const nameEl = root.querySelector("#name");
        const emailEl = root.querySelector("#email");
        const userSel = root.querySelector("#user_id");
        // Name
        const nameVal = (this.state.name || "").trim();
        if (!nameVal) {
            this._markInvalid(nameEl);
            errors.push("missing_name");
        }
        // Email
        const emailVal = (this.state.email || "").trim();
        const emailOk = Boolean(emailVal) && /[^\s@]+@[^\s@]+\.[^\s@]+/.test(emailVal);
        if (!emailVal) {
            this._markInvalid(emailEl);
            errors.push("missing_email");
        } else if (!emailOk) {
            this._markInvalid(emailEl);
            errors.push("invalid_email");
        }
        // Type and user
        if (!this.state.type_id) errors.push("missing_type");
        if (this.state.type_id && !this.state.user_id) {
            this._markInvalid(userSel);
            errors.push("missing_user");
        }
        return errors;
    }

    _validateQuestions(root) {
        const errors = [];
        for (const q of this.state.questions) {
            if (!q.required) continue;
            const key = `qa_${q.id}`;
            if (q.field_type === "boolean") {
                const checked = root.querySelector(`input[name="${key}"]:checked`);
                if (!checked) {
                    root.querySelectorAll(`input[name="${key}"]`).forEach((el) =>
                        this._markInvalid(el)
                    );
                    errors.push(`missing_${key}`);
                }
                continue;
            }
            const el = root.querySelector(`#${key}`);
            const val = el ? String(el.value || "").trim() : "";
            if (!val) {
                this._markInvalid(el);
                errors.push(`missing_${key}`);
            }
        }
        return errors;
    }
}

export default RBookingForm;
