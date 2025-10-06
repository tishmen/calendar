/** @odoo-module */

import { registry } from "@web/core/registry";

// Slim tour: visit /rbooking, ensure the form renders, and interact with fields
registry.category("web_tour.tours").add("web_resource_booking_public_tour", {
    url: "/rbooking",
    test: true,
    steps: () => [
        {
            content: "Form root should be mounted",
            trigger: "#rbooking-app",
        },
        {
            content: "Type select appears",
            trigger: "#rbooking-app select#type_id",
        },
        {
            content: "Pick first booking type",
            trigger: "#rbooking-app select#type_id",
            run: "selectByIndex 1",
        },
        {
            content: "User options loaded",
            // Wait until the user select is enabled and has at least one real option
            trigger: "#rbooking-app select#user_id:not(:disabled):has(option[value])",
            timeout: 20000,
            run: () => {},
        },
        {
            content: "Pick first user",
            trigger: "#rbooking-app select#user_id:not(:disabled)",
            run: "selectByIndex 1",
        },
        {
            content: "Fill name",
            trigger: "#rbooking-app input#name",
            run: "edit Guest From Tour",
        },
        {
            content: "Fill email",
            trigger: "#rbooking-app input#email",
            run: "edit guest.tour@example.com",
        },
        {
            content: "Submit form",
            trigger: "#rbooking-app button.btn.btn-primary:not([disabled])",
            run: "click",
            expectUnloadPage: true,
        },
    ],
});
