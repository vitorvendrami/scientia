from rest_framework import serializers
from django.contrib.auth.models import User
from .models import GenerateEnvironment


class GenerateEnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateEnvironment
        fields = ['p_tuple',
                  'i_tuple',
                  'j_tuple',
                  'tc_tuple',
                  'pc_tuple',
                  'fc_tuple',
                  'demand_tuple',
                  "space_tuple",
                  ]


class GenerateEnvironmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateEnvironment
        fields = ['uuid',]


class GenerateEnvironmentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateEnvironment
        exclude = ['id', ]