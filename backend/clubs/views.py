from .models import Club
from rest_framework import viewsets
from .serializers import ClubSerializer, PublicClubSerializer, ClubWhyJoinSerializer
from rest_framework.permissions import AllowAny, IsAdminUser

class ClubViewSet(viewsets.ModelViewSet):
    queryset = Club.objects.all()
    serializer_class = ClubSerializer

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_serializer_class(self):
        if not self.request.user.is_authenticated:
            return PublicClubSerializer
        return ClubSerializer


class ClubWhyJoinViewSet(viewsets.ModelViewSet):
    serializer_class = ClubWhyJoinSerializer

    ### NOTE: IF MULTIPLE INSTANCES ARE TO BE SUPPORTED HERE, JUST WRAP THESE IN FOR LOOPS
    def perform_create(self, serializer):
        """
        INSERT instance
        |||||||||||||||||||||||||||||||||||  OLD
                              ^              MOVE HERE
        ||||||||||||||||||||||SSSSSSSSSSSSS  IDENTIFY SHIFT
        |||||||||||||||||||||| SSSSSSSSSSSSS SHIFT RIGHT
        ||||||||||||||||||||||N||||||||||||| NEW
        """
        index = serializer.validated_data.get("index") 
        model_class = self.get_queryset().model
        change = model_class.objects.filter(index__gte=index)
        # with transaction.atomic() {
        for instance in change:
            instance.index += 1
            instance.save()
        # }

        serializer.save()

    def perform_update(self, serializer):
        index = serializer.validated_data.get("index") 
        self_inst = self.get_object()
        model_class = self.get_queryset().model

        if index > self_inst.index:
            """
            move instance to RIGHT
            |||||||||||||O||||||||||||||||||||| OLD
                                  ^             MOVE HERE
            ||||||||||||| SSSSSSSSS|||||||||||| IDENTIFY SHIFT
            |||||||||||||SSSSSSSSS |||||||||||| SHIFT RIGHT
            ||||||||||||||||||||||N|||||||||||| NEW
            """

            down = model_class.objects.filter(index_gt=self_inst.index, index_lt=index)
            # with transaction.atomic() {
            for instance in down:
                instance.index -= 1
                instance.save()
            # }

        elif index < self_inst.index:
            """
            move instance to LEFT
            ||||||||||||||||||||||O|||||||||||| OLD
                         ^                      MOVE HERE
            |||||||||||||SSSSSSSSS |||||||||||| IDENTIFY SHIFT
            ||||||||||||| SSSSSSSSS|||||||||||| SHIFT LEFT
            |||||||||||||N||||||||||||||||||||| NEW
            """

            up = model_class.objects.filter(index__gte=index, index_lt=self_inst.index)
            # with transaction.atomic() {
            for instance in up:
                instance.index += 1
                instance.save()
            # }
        
        serializer.save()

    def perform_destroy(self, instance):
        """
        DESTROY instance
        |||||||||||||O||||||||||||||||||||| OLD
        ||||||||||||| ||||||||||||||||||||| REMOVE OLD
        ||||||||||||| SSSSSSSSSSSSSSSSSSSSS IDENTIFY SHIFT
        |||||||||||||SSSSSSSSSSSSSSSSSSSSS  SHIFT LEFT
        ||||||||||||||||||||||||||||||||||  NEW
        """

        self_inst = self.get_object()
        model_class = self.get_queryset().model

        change = model_class.objects.filter(index__gt=self_inst.index)
        for instance in change:
            instance.index -= 1
            instance.save()
        