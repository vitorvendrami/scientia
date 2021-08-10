from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .serializers import GenerateEnvironmentListSerializer, GenerateEnvironmentRetrieveSerializer, GenerateEnvironmentSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import GenerateEnvironment
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


class GenerateEnvironmentViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    serializer_class = GenerateEnvironmentSerializer
    filter_backends = (SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ('uuid',)
    lookup_field = 'uuid'
    queryset = GenerateEnvironment.objects.all()

    def list(self, request):
        """
            Create and return a new `Snippet` instance, given the validated data.
        """
        queryset = GenerateEnvironment.objects.all()
        serializer = GenerateEnvironmentListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, uuid=None):

        try:
            queryset = GenerateEnvironment.objects.all()

            env = get_object_or_404(queryset, uuid=uuid)
            results = env.run(uuid)

            serializer = GenerateEnvironmentRetrieveSerializer(env)
            results.update(serializer.data)

        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(results, status=status.HTTP_200_OK)

    def create(self, request):
        try:

            p_tuple = request.data['p_tuple']
            i_tuple = request.data['i_tuple']
            j_tuple = request.data['j_tuple']
            tc_tuple = request.data['tc_tuple']
            pc_tuple = request.data['pc_tuple']
            fc_tuple = request.data['fc_tuple']
            demand_tuple = request.data['demand_tuple']
            space_tuple = request.data['space_tuple']

            env = GenerateEnvironment.objects.create(
                p_tuple=p_tuple,
                i_tuple=i_tuple,
                j_tuple=j_tuple,
                tc_tuple=tc_tuple,
                pc_tuple=pc_tuple,
                fc_tuple=fc_tuple,
                demand_tuple=demand_tuple,
                space_tuple=space_tuple
            )

        except Exception as e:
            return Response(
                {"error": "failed to create Environment"},
                status=status.HTTP_400_BAD_REQUEST)

        else:
            serializer = GenerateEnvironmentRetrieveSerializer(env)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

    def destroy(self, request, *args, **kwargs):
        try:
            uuid = kwargs['uuid']
            queryset = GenerateEnvironment.objects.all()

            env = get_object_or_404(queryset, uuid=uuid)
            env.delete()

        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
