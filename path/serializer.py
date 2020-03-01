from rest_framework import serializers
from .models import Path, UserBase
from .util import get_md5, get_salt, parse_path


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserBase
        fields = ['salt']


class PathListSerializers(serializers.ModelSerializer):
    """
    用于获取所有路径和创建新的路径
    """

    class Meta:
        model = Path
        fields = (
            'id', 'title', 'desc', 'author', 'user_like', 'create_time', 'path', 'uid', 'username', 'path_pc',
            'path_pe', 'last_download')
        extra_kwargs = {
            "id": {"read_only": True},
            "user_like": {"read_only": True},
            'create_time': {'read_only': True},
            'last_download': {'read_only': True}
        }

    user_like = serializers.SerializerMethodField(read_only=True)  # 点赞数

    uid = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    path = serializers.CharField(required=False, write_only=True, default="{}")
    path_pc = serializers.HiddenField(required=False, write_only=True, default="{}")
    path_pe = serializers.HiddenField(required=False, write_only=True, default="{}")

    def get_user_like(self, obj):
        try:
            return obj.user_like.all().count()
        except AttributeError:
            return 0

    def validate(self, attrs):
        attrs['username'] = attrs['username'].lower()
        path = parse_path(attrs['path'], attrs['title'], attrs['desc'])
        attrs['path_pe'] = path['pe']
        attrs['path_pc'] = path['pc']
        del attrs['path']
        return attrs

    def save(self, **kwargs):
        attrs = self.validated_data
        user = UserBase.objects.get_or_create(uid=attrs['uid'], username=attrs['username'],
                                              salt=get_salt(attrs['uid'], attrs['username']))[0]
        Path.objects.create(
            user=user,
            author=attrs['author'],
            title=attrs['title'],
            desc=attrs['desc'],
            path_pc=attrs['path_pc'],
            path_pe=attrs['path_pe']
        )


class PathGetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = ('id', 'title', 'desc', 'path_pc', 'path_pe', 'create_time', 'last_download')


class LikeSerializers(serializers.Serializer):
    uid = serializers.IntegerField()
    username = serializers.CharField()  # 用户名
    salt = serializers.CharField()  # 盐

    id = serializers.IntegerField()  # 喜欢的编号

    def validate(self, attrs):
        attrs['username'] = attrs['username'].lower()
        if get_salt(attrs['uid'], attrs['username']) != attrs['salt']:
            raise serializers.ValidationError("用户验证失败")
        try:
            Path.objects.get(id=attrs['id'])
        except Exception:
            raise serializers.ValidationError("对应id不存在")

        user = UserBase.objects.get_or_create(uid=attrs['uid'],
                                              username=attrs['username'],
                                              salt=attrs['salt'])[0]
        path = Path.objects.get(id=attrs['id'])
        if user in path.user_like.all():
            raise serializers.ValidationError("test")
        attrs['_path'] = path
        attrs['_user'] = user
        return attrs

    def save(self):
        user = self.validated_data['_user']
        path = self.validated_data['_path']
        path.user_like.add(user)
