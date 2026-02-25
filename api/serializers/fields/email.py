import re

from rest_framework import serializers


class EmailField(serializers.EmailField):
    def to_internal_value(self, data: str) -> str:
        value = super().to_internal_value(data)

        if value and not self.allow_blank:
            value = value.lower().strip()

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, value):
                raise serializers.ValidationError("invalid_email_format")

            domain = value.split("@")[1]
            if len(domain) < 3 or "." not in domain:
                raise serializers.ValidationError("invalid_email_domain")

        return value
