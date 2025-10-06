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
        });
        this.csrf = this.props.csrf;
        this.usersEndpoint = this.props.usersEndpoint;
        this.startUrl = this.props.startUrl || "/rbooking/start";
        this.questionsEndpoint = this.props.questionsEndpoint || "/rbooking/questions";
        // Preselect type from props if provided, and fetch dependent data
        if (this.props.preselectedTypeId) {
            this.state.type_id = String(this.props.preselectedTypeId);
            // Fire and forget; state updates will re-render when data arrives
            this.onTypeChange();
        }
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
            const root = this.el;
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
}

export default RBookingForm;
