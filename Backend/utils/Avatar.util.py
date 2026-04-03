# ======================== #
# Utility Functions
# ======================== #
def generate_avatar(name):
    """
    Generate avatar URL using user's name initials.
    Uses Dicebear API (no authentication needed).
    """
    try:
        if not name:
            return "https://api.dicebear.com/7.x/initials/svg?seed=U"
        # Extract initials
        parts = name.split()
        initials = "".join([part[0].upper() for part in parts if part])
        # Use Dicebear API
        return f"https://api.dicebear.com/7.x/initials/svg?seed={initials}&scale=70"
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        return "https://api.dicebear.com/7.x/avataaars/svg?seed=default"