"""
Serializers for LLM API
"""
from rest_framework import serializers

class GenerateRequestSerializer(serializers.Serializer):
    """Serializer for text generation requests"""
    prompt = serializers.CharField(max_length=4096, help_text="Input text prompt")
    model = serializers.CharField(
        max_length=50, 
        required=False, 
        help_text="Model to use (defaults to current loaded model)"
    )
    parameters = serializers.DictField(
        required=False,
        help_text="Generation parameters (temperature, top_p, max_length, etc.)"
    )
    
    def validate_parameters(self, value):
        """Validate generation parameters"""
        if value is None:
            return {}
        
        allowed_params = {'temperature', 'top_p', 'max_length', 'do_sample'}
        invalid_params = set(value.keys()) - allowed_params
        
        if invalid_params:
            raise serializers.ValidationError(
                f"Invalid parameters: {', '.join(invalid_params)}. "
                f"Allowed: {', '.join(allowed_params)}"
            )
        
        # Validate parameter ranges
        if 'temperature' in value:
            temp = value['temperature']
            if not (0.0 <= temp <= 2.0):
                raise serializers.ValidationError("Temperature must be between 0.0 and 2.0")
        
        if 'top_p' in value:
            top_p = value['top_p']
            if not (0.0 <= top_p <= 1.0):
                raise serializers.ValidationError("top_p must be between 0.0 and 1.0")
        
        if 'max_length' in value:
            max_len = value['max_length']
            if not (1 <= max_len <= 4096):
                raise serializers.ValidationError("max_length must be between 1 and 4096")
        
        return value

class ModelInfoSerializer(serializers.Serializer):
    """Serializer for model information"""
    name = serializers.CharField()
    loaded = serializers.BooleanField()
    config = serializers.DictField(required=False)