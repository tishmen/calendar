import {mount} from "@odoo/owl";
import {getTemplate} from "@web/core/templates";
import publicWidget from "@web/legacy/js/public/public_widget";
import RBookingForm from "./rbooking_form.esm";

publicWidget.registry.RBookingFormWidget = publicWidget.Widget.extend({
    selector: "#rbooking-app",
    start() {
        const root = this.el;
        const csrf =
            window.odoo && window.odoo.csrf_token
                ? window.odoo.csrf_token
                : (document.querySelector('input[name="csrf_token"]') || {}).value;
        let types = [];
        const dataSelect = root.querySelector("#rbooking-types-data");
        if (dataSelect) {
            types = Array.from(dataSelect.querySelectorAll("option")).map((opt) => ({
                id: opt.value,
                display_name: opt.dataset.name,
            }));
        }
        return mount(RBookingForm, root, {
            getTemplate,
            props: {
                csrf,
                usersEndpoint: root.dataset.usersEndpoint,
                questionsEndpoint:
                    root.dataset.questionsEndpoint || "/rbooking/questions",
                startUrl: "/rbooking/start",
                types,
            },
        });
    },
});

export default publicWidget.registry.RBookingFormWidget;
