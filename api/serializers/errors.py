from rest_framework import serializers


class ErrorResponseSerializer(serializers.Serializer[dict[str, str]]):
    code = serializers.IntegerField(help_text="HTTP status code", read_only=True)
    detail = serializers.CharField(help_text="Error detail/message", read_only=True)
    attr = serializers.CharField(
        required=False,
        allow_null=True,
        help_text="Field name or attribute that the error relates to",
        read_only=True,
    )
