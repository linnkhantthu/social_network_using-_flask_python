from flask_marshmallow import Schema, fields


class PostSchema(Schema):
    id = fields.fields.Integer()
    title = fields.fields.String()
    date_posted = fields.fields.DateTime()
    content = fields.fields.String()
    poll_data = fields.fields.Dict()
    tag = fields.fields.String()
    user_id = fields.fields.String()


