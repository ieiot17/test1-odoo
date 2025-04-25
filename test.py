import xmlrpc.client
import traceback

#Use the secret password from the credentials file
#with open("./credentials", "r") as file:
password = "8d6c4983d9dacbed55eca3f6361f5cbbe3b13cf8"

# 🔹 Odoo Server Configuration
url = "http://192.168.56.105:8039/"  #Odoo server URL
db = "custom"  # database name
username = "service"  # Odoo username

# 🔹 Authenticate with Odoo
try:
    # 🔹 Authenticate with Odoo
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("❌ Authentication failed. Check your Odoo credentials.")
        exit()

    print(f"✅ Authenticated as UID {uid}")

    # 🔹 Connect to Odoo models
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # 🔹 Fetch all attachment IDs
    attachment_ids = models.execute_kw(db, uid, password, 'ir.attachment', 'search', [[]])
    
    
# 📦 Read res_model, name, id fields
    attachments = models.execute_kw(
        db, uid, password,
        'ir.attachment', 'read',
        [attachment_ids],
        {'fields': ['id', 'name', 'res_model']}
    )

    # 🖨️ Print results
    for att in attachments:
        print(f"ID: {att['id']}, Name: {att['name']}, res_model: {att.get('res_model')}")

    if not attachment_ids:
        print("ℹ️ No attachments found in the database.")
        exit()

    print(f"⚠️ Warning: This will delete {len(attachment_ids)} attachments permanently!")

    # 🔹 Delete all attachments
    models.execute_kw(db, uid, password, 'ir.attachment', 'unlink', [attachment_ids])
    print(f"✅ Successfully deleted {len(attachment_ids)} attachments from Odoo.")

except Exception as e:
    print("❌ An error occurred during execution:")
    traceback.print_exc()