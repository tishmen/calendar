/** @odoo-module */

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
        });
        this.csrf = this.props.csrf;
        this.usersEndpoint = this.props.usersEndpoint;
        this.startUrl = this.props.startUrl || "/rbooking/start";
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
        if (!this.state.type_id) return;
        this.state.loading = true;
        try {
            const url = `${this.usersEndpoint}?type_id=${encodeURIComponent(this.state.type_id)}`;
            const resp = await fetch(url, {headers: {Accept: "application/json"}});
            const data = await resp.json();
            this.state.users = Array.isArray(data.users) ? data.users : [];
        } catch {
            this.state.users = [];
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
        document.body.appendChild(form);
        form.submit();
    }
}

export default RBookingForm;
