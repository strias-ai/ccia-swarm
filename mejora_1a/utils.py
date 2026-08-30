import sys

def get_agent_capabilities(agent_id):
    # Simulación de la obtención de capacidades del agente
    # En un entorno real, esta función podría consultar una base de datos o un servicio externo
    capabilities = {
        'agent1': ['completar proyectos', 'crear proyectos'],
        'agent2': ['crear proyectos', 'gestionar proyectos'],
        'agent3': ['completar proyectos', 'gestionar proyectos']
    }
    return capabilities.get(agent_id, [])

def analyze_agent_info(agent_id):
    # Simulación de la recopilación y análisis de información
    # En un entorno real, esta función podría realizar análisis más complejos
    capabilities = get_agent_capabilities(agent_id)
    print(f"Agent {agent_id} needs the following capabilities: {', '.join(capabilities)}")

if __name__ == "__main__":
    try:
        agent_id = sys.argv[1] if len(sys.argv) > 1 else 'agent1'
        analyze_agent_info(agent_id)
    except IndexError:
        print("Usage: python utils.py <agent_id>")
```

Este código define dos funciones: `get_agent_capabilities` y `analyze_agent_info`. La primera función simula la obtención de las capacidades de un agente, mientras que la segunda función recopila y analiza esta información. El script se ejecuta desde la línea de comandos y toma el identificador del agente como argumento. Si no se proporciona un identificador, se asume que el agente es 'agent1'.