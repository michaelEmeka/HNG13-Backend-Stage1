from rest_framework import views, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import *
from .models import AnalyzedString
import hashlib

class CreateStringAnalysisView(GenericAPIView):
    serializer_class = CreateStringAnalysisSerializer
    queryset = AnalyzedString.objects.all()

    def post(self, request):
        json_string = request.data
        string = json_string["value"]
        hash_object = hashlib.sha256(string.encode())
        string_sha_256 = hash_object.hexdigest()

        if "value" not in json_string.keys() or len(json_string.keys()) != 1:
            return Response({'error': 'Invalid request body or missing "value" field'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(string, str) or string == "":
            return Response(
                {'error': 'Invalid data type for "value" (must be string)'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        if AnalyzedString.objects.filter(sha256_hash=string_sha_256).exists():
            return Response(
                {"error": "String already exists in the system"},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = self.serializer_class(data=json_string)

        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "id": instance.sha256_hash,
                "value": instance.original_string,
                "properties": {
                    "length": instance.length,
                    "is_palindrome": instance.is_palindrome,
                    "unique_characters": instance.unique_characters,
                    "word_count": instance.word_count,
                    "sha256_hash": instance.sha256_hash,
                    "character_frequency_map": instance.character_frequency_map
                },
                "created_at": instance.created_at
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response({'error': serializer.errors})


# 2. Get Specific String
class GetStringAnalysis(GenericAPIView):
    serializer_class = GetStringAnalysisSerializer
    # model = AnalyzedString

    def get(self, request, *args, **kwargs):
        value = kwargs.get("value")

        if AnalyzedString.objects.filter(original_string=value).exists():
            instance = AnalyzedString.objects.get(original_string=value)
            return Response(
                {
                    "id": instance.sha256_hash,
                    "value": instance.original_string,
                    "properties": {
                        "length": instance.length,
                        "is_palindrome": instance.is_palindrome,
                        "unique_characters": instance.unique_characters,
                        "word_count": instance.word_count,
                        "sha256_hash": instance.sha256_hash,
                        "character_frequency_map": instance.character_frequency_map,
                    },
                    "created_at": instance.created_at,
                },
                status=status.HTTP_200_OK,
            )
        return Response({"error": "String does not exist in the system"}, status=status.HTTP_404_NOT_FOUND)


