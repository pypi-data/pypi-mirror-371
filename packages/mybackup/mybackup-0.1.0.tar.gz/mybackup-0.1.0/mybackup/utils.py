def is_valid_domain(domain):
    return isinstance(domain, str) and "." in domain and not domain.startswith("http")
