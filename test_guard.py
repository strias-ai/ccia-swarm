from verify_subscription import check_user_subscription

users = ["student@ccia.edu", "unpaid_user@ccia.edu"]

for user in users:
    has_access = check_user_subscription(user)
    status_icon = "✅" if has_access else "❌"
    print(f"{status_icon} Usuario: {user} | Acceso Prémium: {has_access}")
