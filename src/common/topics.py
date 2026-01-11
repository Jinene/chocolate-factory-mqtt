def topic(site: str, line: str, step: str, machine: str, msg_type: str) -> str:
    # Professional topic namespace:
    # factory/<site>/<line>/<step>/<machine>/<message_type>
    return f"factory/{site}/{line}/{step}/{machine}/{msg_type}"
