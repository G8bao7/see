#coding=utf8
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.baseviews import BaseView
from utils.baseviews import ReturnFormatMixin as res
from utils.permissions import IsSuperUser
from sqlmng.mixins import FixedDataMixins, CheckConn, HandleInceptionSettingsMixins
from sqlmng.data import variables
from sqlmng.serializers import *
from sqlmng.models import *

class ForbiddenWordsViewSet(BaseView):
    '''
        设置SQL语句中需拦截的字段
    '''
    queryset = ForbiddenWords.objects.all()
    serializer_class = ForbiddenWordsSerializer
    permission_classes = [IsSuperUser]

class StrategyViewSet(BaseView):
    '''
        设置审批策略
    '''
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsSuperUser]

class PersonalSettingsViewSet(BaseView):
    '''
        审核工单的用户个性化设置
    '''
    serializer_class = PersonalSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        # save user
        request_data = request.data
        instance = request.user
        user_serializer = self.serializer_class(instance, data={'leader':request_data.get('leader')})
        user_serializer.is_valid()
        user_serializer.save()
        cluster = request_data.get('cluster')
        dbs = request_data.get('dbs')
        env = request_data.get('env')
        alter_qs = instance.dbconf_set.filter(cluster=cluster, env=env)
        for obj in alter_qs:
            instance.dbconf_set.remove(obj)
        for db_id in dbs:
            instance.dbconf_set.add(db_id)
        return Response(res.get_ret())

class InceptionVariablesViewSet(FixedDataMixins, HandleInceptionSettingsMixins, BaseView):
    '''
        Inception 变量
    '''
    serializer_class = InceptionVariablesSerializer
    search_fields = ['name']
    source_data = variables

    def create(self, request, *args, **kwargs):
        self.set_variable(request)
        return Response(res.get_ret())

class InceptionConnectionViewSet(BaseView):
    '''
        Inception 连接
    '''
    queryset = InceptionConnection.objects.all()
    serializer_class = InceptionConnectionSerializer
    permission_classes = [IsSuperUser]

class InceptionBackupView(HandleInceptionSettingsMixins, APIView):

    def get(self, request, *args, **kwargs):
        ret = res.get_ret()
        ret['data'] = self.get_inception_backup()
        return Response(ret)

class ConnectionCheckView(CheckConn, APIView):

    def post(self, request, *args, **kwargs):
        res = self.check(request)
        return Response(res)
