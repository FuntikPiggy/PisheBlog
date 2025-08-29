from django.contrib.auth import get_user_model
from django.forms import ModelChoiceField, ModelMultipleChoiceField
from django import forms

from recipes.models import Recipe, User, Tag, Ingredient

# class ProfileEditForm(UserChangeForm):
#     """Форма редактирования профиля на основании формы библиотеки."""
#
#     class Meta:
#         model = User
#
#         fields = ('username', 'first_name', 'last_name', 'email')



User = get_user_model()
# class NameField(ModelChoiceField):
#     def label_from_instance(self, obj):
#         return "My Object #%i" % obj.id


class AuthorField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.username


class NameMultiField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RecipeAdminForm(forms.ModelForm):
    """Форма рецепта на основании модели рецепта для админки."""

    name = AuthorField(queryset=Recipe.objects.all())
    author = AuthorField(queryset=User.objects.all(), label='Автор')
    tags = NameMultiField(queryset=Tag.objects.all(), label='Теги')
    ingredients = NameMultiField(queryset=Ingredient.objects.all(), label='Ингредиенты')

    class Meta:
        model = Recipe
        fields = '__all__'
        readonly_fields = fields
        # widgets = {
        #     "name": Textarea(attrs={"cols": 80, "rows": 20}),
        # }

    # def __init__(self, *args, **kwargs):
    #     super(__class__, self).__init__(*args, **kwargs)
    #     for field in ['author', 'tags', 'ingredients']:
    #         self.fields[field].label_from_instance = self.label_from_instance
    #
    # @staticmethod
    # def label_from_instance(obj):
    #     return getattr(obj, 'name', None) or obj.username
    #
    # def clean_name(self):
    #     return '1'
    #
    # def clean_tags(self):
    #     return self.name
    #     # labels = {
    #     #     "name": _("Writer"),
    #     # }
    #
