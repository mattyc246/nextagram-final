from models.base_model import BaseModel
import peewee as pw
import re
from config import S3_HOST_URL
from werkzeug.security import generate_password_hash
from playhouse.hybrid import hybrid_property, hybrid_method


class User(BaseModel):
    email = pw.CharField(null=False)
    full_name = pw.CharField(null=False)
    username = pw.CharField(unique=True, null=False)
    password = pw.CharField(null=False)
    website = pw.CharField(null=True)
    bio = pw.TextField(null=True)
    phone_number = pw.CharField(null=True)
    profile_picture = pw.CharField(null=True)
    private = pw.BooleanField(default=False)

    def validate(self):
        email_valid = re.match(r"[^@]+@[^@]+\.[^@]+", self.email)
        password_valid = re.match(r"^[a-zA-Z]\w{3,14}$", self.password)
        duplicate_username = User.get_or_none(User.username == self.username)

        if not User.get_or_none(User.id == self.id):

            if len(self.full_name) < 1:
                self.errors.append('Please provide a name!')

            if not email_valid:
                self.errors.append('Invalid Email Provided')

            if duplicate_username:
                self.errors.append('Username already taken!')

            if password_valid:
                self.password = generate_password_hash(self.password)
            else:
                self.errors.append('Password is not valid, min 6 characters')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    @hybrid_property
    def profile_url(self):
        from flask import url_for
        if self.profile_picture:
            return f"{S3_HOST_URL}/{self.profile_picture}"
        else:
            return url_for('static', filename="images/profile-placeholder.png")

    @hybrid_property
    def has_posts(self):
        from models.image import Image
        images = Image.select().where(Image.user_id == self.id)
        return True if len(images) > 0 else False

    @hybrid_method
    def is_following(self, user):
        from models.follower_following import FollowerFollowing
        follow = FollowerFollowing.get_or_none(
            (FollowerFollowing.fan_id == self.id) & (FollowerFollowing.idol_id == user.id))
        return False if not follow or not follow.approved else True

    @hybrid_property
    def approved_follows(self):
        from models.follower_following import FollowerFollowing
        follows = User.select().join(
            FollowerFollowing, on=(User.id == FollowerFollowing.idol_id)
        ).where(
            (FollowerFollowing.fan_id == self.id) &
            (FollowerFollowing.approved == True)
        )
        return follows

    @hybrid_property
    def pending_follows(self):
        from models.follower_following import FollowerFollowing
        follows = FollowerFollowing.select().where(
            (FollowerFollowing.idol_id == self.id) &
            (FollowerFollowing.approved == False)
        )
        return follows

    @hybrid_property
    def has_pending_follows(self):
        from models.follower_following import FollowerFollowing
        follows = FollowerFollowing.select().where(
            (FollowerFollowing.idol_id == self.id) &
            (FollowerFollowing.approved == False)
        )
        return True if len(follows) > 0 else False
