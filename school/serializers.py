from rest_framework import serializers
from .models import  SchoolGrade



class SchoolGradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolGrade
        fields = '__all__'
        ref_name = 'SchoolSchoolGrade'

