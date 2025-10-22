from rest_framework import views, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.core.exceptions import FieldError
from .serializers import *
from .models import AnalyzedString
from .utils import NLP, get_filtered_queryset
import hashlib


class CreateStringAnalysisView(GenericAPIView):
    #CreateStringAnalysisView or
    #GetStringsByFilterView
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
        
    # Get All Strings with Filtering
    def get(self, request, *args, **kwargs):
        filters = request.query_params
        filters = filters.copy()
        print(filters)
        try:
            valid_query_pararmeters = ["is_palindrome", "min_length", "max_length", "word_count", "contains_character"]

            min_length = int(filters["min_length"])
            max_length = int(filters["max_length"])
            word_count = int(filters["word_count"])
            contains_character = filters["contains_character"]
            is_palindrome = filters["is_palindrome"]
            print(is_palindrome)
            print(type(is_palindrome))
            # print(filters["min_length"])
            if (
                not isinstance(contains_character, str)
                or len(contains_character) != 1
                or (is_palindrome != "true" and is_palindrome != "false")
            ):
                return Response(
                    {"error": "Invalid query parameter values or typeskm"}, status=status.HTTP_400_BAD_REQUEST
                )

            for key in filters.keys():
                if key not in valid_query_pararmeters:
                    return Response(
                    {"error": "Invalid query parameter values or types"}, status=status.HTTP_400_BAD_REQUEST
                )
                    
            is_palindrome = True if is_palindrome == "true" else False
            
            filters = {
                "is_palindrome": is_palindrome,
                "word_count": word_count,
                }
            response = {}
            data = []
            if AnalyzedString.objects.filter(**filters).exists():
                queryset = AnalyzedString.objects.filter(**filters)

                for instance in queryset:
                    if (
                        instance.length in range(min_length, max_length)
                        and contains_character in instance.original_string
                    ):
                        data.append(
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
                        })
            response["data"] = data
            response["count"] = len(data)
            response["filters_applied"] = {
                "is_palindrome": is_palindrome,
                "min_length": min_length,
                "max_length": max_length,
                "word_count": word_count,
                "contains_character": contains_character,
            }

            return Response(response, status=status.HTTP_200_OK)

        except (TypeError, ValueError, KeyError, FieldError) as e:
            print(e)
            return Response({"error": "Invalid query parameter values or types key"}, status=status.HTTP_400_BAD_REQUEST)

# 2. Get Specific String
class Get_DeleteStringAnalysis(GenericAPIView):
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

    def delete(self, request, *args, **kwargs):
        value = kwargs.get("value")
        if AnalyzedString.objects.filter(original_string=value).exists():
            AnalyzedString.objects.get(original_string=value).delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "String does not exist in the system"}, status=status.HTTP_404_NOT_FOUND)



##Natural Language Filtering
class NaturalLanguageFilterView(GenericAPIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query")
        filter = NLP(query)

        data = []
        response = {}

        if query is None or query == "":
            return Response({"error": "Unable to parse natural language query"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            queryset = get_filtered_queryset(filter)
        except:
            return Response(
                {"error": "Query parsed but resulted in conflicting filters"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        for instance in queryset:
            data.append(
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
            })
        response["data"] = data
        response["count"] = len(data)
        response["interpreted_query"] = {
            "original": query,
            "parsed_filters": {}
        }
        for key, value in filter.items():
            if value is not None:
                response["interpreted_query"]["parsed_filters"][key] = value
        return Response(response, status=status.HTTP_200_OK)
