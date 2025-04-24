from odoo import models, fields

class CustomerProfile(models.Model):
    _inherit = 'res.partner'

    # Name & Company
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    preferred_name = fields.Char(string="Preferred Name/Nickname")
    same_as_billing = fields.Boolean(string="Same as Billing Address")

    # Preferences
    marketing_opt_out = fields.Boolean(string="Marketing Opt-Out")
    sms_opt_out = fields.Boolean(string="SMS/TXT Opt-Out")
    travel_interested_client = fields.Boolean(string="Travel-Interested Client")

    # Additional Info
    celebrity_name = fields.Char(string="Celebrity Name")
    salesperson = fields.Char(string="Salesperson")  # Fixed the incorrect placement

    marketing_point_of_contact = fields.Selection([
        ('tbd', 'TBD'),
    ], string="Marketing Point of Contact")

    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deceased', 'Deceased'),
        ('terminated', 'Terminated'),
    ], string="Status")

    # Admin Info
    salesforce_account_id = fields.Char(string="Salesforce Account ID")
    starting_balance = fields.Float(string="Starting Balance")
    
    invoice_sending_method = fields.Selection([
        ('email', 'Email'),
        ('physical', 'Physical'),
        ('both', 'Both'),
        ('none', 'No Statement'),
    ], string="Invoice sending")
