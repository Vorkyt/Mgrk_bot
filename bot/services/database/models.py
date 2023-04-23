from tortoise import fields
from tortoise.models import Model

from ...bot import bot
from ...utils.enums import Alignment


class BotUser(Model):
    id = fields.IntField(pk=True, unique=True)  # telegram user id
    username = fields.TextField(null=True)
    full_name = fields.TextField()


class ReplyMenu(Model):
    id = fields.IntField(pk=True, unique=True)

    parent: fields.ForeignKeyNullableRelation["ReplyMenu"] = fields.ForeignKeyField(
        "models.ReplyMenu", related_name="children", null=True
    )
    children: fields.ReverseRelation["ReplyMenu"]

    name = fields.TextField(null=True)
    alignment = fields.IntEnumField(Alignment, default=Alignment.vertical)
    position = fields.IntField(null=True)
    back_button_text = fields.TextField(null=True)

    inline_menu: fields.OneToOneRelation["InlineMenu"] = fields.OneToOneField(
        "models.InlineMenu", related_name="main_menu"
    )

    @classmethod
    async def get_root_menu(cls):
        root_menu = (
            await cls.filter(id=1)
            .prefetch_related("children", "parent", "inline_menu")
            .first()
        )

        if root_menu:
            return root_menu

        inline_menu = await InlineMenu.create()
        root_menu = await ReplyMenu.create(id=1, inline_menu=inline_menu)

        # await root_menu.fetch_related("message_menu", "children", "parent")
        return root_menu


class InlineMenu(Model):
    id = fields.IntField(pk=True, unique=True)

    parent: fields.ForeignKeyNullableRelation["InlineMenu"] = fields.ForeignKeyField(
        "models.InlineMenu", related_name="children", null=True
    )
    children: fields.ReverseRelation["InlineMenu"]

    name = fields.TextField(null=True)
    text = fields.TextField(null=True)
    url = fields.TextField(null=True)
    back_button_text = fields.TextField(null=True)
    alignment = fields.IntEnumField(Alignment, default=Alignment.horizontal)
    position = fields.IntField(null=True)

    reply_menu: fields.OneToOneRelation["ReplyMenu"]
    file: fields.OneToOneNullableRelation["MessageFile"]


class MessageFile(Model):
    id = fields.IntField(pk=True, unique=True)
    filename = fields.TextField()
    bytes = fields.BinaryField()
    inline_menu: fields.OneToOneRelation["InlineMenu"] = fields.OneToOneField(
        "models.InlineMenu", related_name="file"
    )
