from rest_framework import serializers
from app.models import StudentGroup
from rest_framework import viewsets
from rest_framework import permissions


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StudentGroup
        fields = ['id', 'name']


class GroupViewSet(viewsets.ModelViewSet):
    queryset = StudentGroup.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
