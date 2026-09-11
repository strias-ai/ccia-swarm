
def render_bounty_card(bounty_id, reward):
    if not bounty_id:
        return None
    return f"Card {bounty_id} - Reward: {reward} USD"

assert render_bounty_card('B123', 500) == 'Card B123 - Reward: 500 USD'
print('✅ Test de componente superado')
