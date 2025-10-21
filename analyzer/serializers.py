from rest_framework import serializers
from .models import AnalyzedString
from django.utils.timezone import timezone
import hashlib


class CreateStringAnalysisSerializer(serializers.Serializer):
    value = serializers.CharField()

    def create(self, validated_data):

        print(validated_data)
        string_data = validated_data.get("value")

        hash_object = hashlib.sha256(string_data.encode())

        string_sha_256 = hash_object.hexdigest()

        string_length = len(string_data)

        word_count = len(string_data.split())

        ##is pallindrome
        is_palindrome = False

        sentence = string_data
        sentence_rev = "".join(reversed(sentence))
        print(sentence)
        print(sentence_rev)
        if sentence == sentence_rev:
            print("Pallindrome")
            is_palindrome = True

        # Unique Characters:
        sentence = string_data
        sentence = list(sentence)
        idx_pop = []
        for i in range(len(sentence)):
            c = sentence[i]
            for j in range(i, len(sentence)):
                j += 1
                if j < len(sentence):
                    if sentence[j] == c:
                        if j not in idx_pop:
                            idx_pop.append(j)

        for p in sorted(idx_pop, reverse=True):
            print(p)
            sentence.pop(p)
            #print(sentence.pop(p))

        unique_characters = len(sentence)

        # Characters map
        # using sentence from UniqueCharacters which contains unique characters

        character_frequency_map = {}

        for c in sentence:
            # org_sentence.count(c)
            character_frequency_map[c] = string_data.count(c)

        # Timestamp
        # created_at = f"{timezone.now().strftime('%Y-%m-%dT%H:%M:%SZ')}"

        analyzed_string = AnalyzedString.objects.create(
            sha256_hash=string_sha_256, original_string=string_data,
            length=string_length,
            is_palindrome=is_palindrome,
            unique_characters=unique_characters,
            word_count=word_count,
            character_frequency_map=character_frequency_map)

        return analyzed_string


class GetStringAnalysisSerializer(serializers.Serializer):
    
    pass