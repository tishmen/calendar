{
    "name": "Web Resource Booking",
    "summary": "Public portal view to schedule resource bookings and pick a user",
    "version": "19.0.1.0.0",
    "category": "Appointments",
    "website": "https://github.com/OCA/calendar",
    "author": "Milan Topuzov",
    "license": "AGPL-3",
    "depends": ["resource_booking", "portal"],
    "data": [
        "templates/public_portal.xml",
        "data/cron.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "web_resource_booking/static/src/xml/rbooking_form.xml",
        ],
        "web.assets_frontend_lazy": [
            "web_resource_booking/static/src/js/rbooking_form.esm.js",
            "web_resource_booking/static/src/js/rbooking_public_widget.esm.js",
        ],
        "web.assets_tests": [
            "web_resource_booking/static/src/js/tours/**/*",
        ],
    },
    "application": False,
    "installable": True,
}
