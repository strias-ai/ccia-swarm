import os

ART63_PATH = "/home/k1/ccia_workspace/modules/art_63.py"

with open(ART63_PATH, "r", encoding="utf-8") as f:
    code = f.read()

outbound_trigger = '''
        try:
            import github_outbound_publisher
            github_outbound_publisher.publish_pending_resolutions()
        except Exception as e:
            print(f"⚠️ Error ejecutando publicador saliente: {e}")
'''

if "github_outbound_publisher" not in code:
    code = code.replace(
        'self._update_bounty_state(repo, issue_id, "RESOLVED")',
        'self._update_bounty_state(repo, issue_id, "RESOLVED")\n' + outbound_trigger
    )
    with open(ART63_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Enganche automático de github_outbound_publisher inyectado en art_63.py")
else:
    print("ℹ️ El enganche de github_outbound_publisher ya está activo en art_63.py")
